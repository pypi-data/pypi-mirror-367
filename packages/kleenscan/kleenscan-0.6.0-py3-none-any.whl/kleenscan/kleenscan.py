from time import sleep
import json
import logging
from datetime import datetime
from typing import *


# Custom library imports:
from .lib.http import Ks_http
from .lib.files import *
from .lib.formatting import format_result
from .lib.config import *
from .lib.errors import *
from .lib.log_configure import configure_logging
from .lib.cli_colors import *
from .lib.helpers import *


class Kleenscan:
	@check_types
	def __init__(self, x_auth_token: str, verbose: Optional[bool]=True, max_minutes: Optional[int]=MAX_SCAN_TIME):
		self.ks_http = Ks_http(x_auth_token)
		self.check_token()
		self.logger = configure_logging() if verbose else logging
		self.max_minutes = max_minutes
		self.verbose = verbose



	@staticmethod
	def __handle_out_file(out_file: str, result: str) -> None:
		# Write result to out_file.
		if out_file and type(out_file) == str:
			write_file(out_file, result)



	@staticmethod
	def __sleep_count(count: int) -> int:
		sleep(count)
		if count >= 2:
			count -= 1
		return count



	def check_token(self) -> None:
		api_data = self.ks_http.get_req_json_noerr('https://kleenscan.com/api/v1/get/avlist')
		if api_data['message'] in ('Authentication token is invalid',
			'Invalid authentication token size'
		):
			raise KsInvalidTokenError



	def __get_url_route_token(self, url: str) -> str:
		count = 4
		while True:
			api_data = self.ks_http.get_req_json(url)
			route_token = api_data['data'].get('route_token')
			if route_token:
				return route_token

			# Delay execution.
			count = self.__sleep_count(count)



	def __check_status(self, data: list[dict], checked_avs: list[str], detected_count: int) -> tuple[bool, int]:
		# Flag for keeping track of when avs are finished/not finished scanning.
		finished = True
		for av_dict in data:
			status = av_dict['status']
			av_name = av_dict["avname"]

			# Is the AV vendor still scanning?
			if status in ('pending', 'scanning'):
				finished = False

			# Av is finished and not previously checked.
			elif status == 'ok' and av_name not in checked_avs:
				flag_name = av_dict['output'] if av_dict['flagname'] == 'Completed' else av_dict['flagname']

				# Antivirus did not detect the url/file.
				if flag_name.lower() == 'undetected':
					self.logger.info(f'{SUCCESS_NOTIF} {av_name}: {flag_name}')

				# Issue with AV vendor.
				elif flag_name in ('Scanning results incomplete', 'Unknown'):
					self.logger.info(f'{INFO_NOTIF} {av_name}: {flag_name}')

				# AV detected the file/url.
				else:
					self.logger.info(f'{ERROR_NOTIF} {av_name}: {flag_name}')
					detected_count += 1

				# Append checked AV to prevent redundant computations.
				checked_avs.append(av_name)

		# Return finished flag and detected count.
		return finished, detected_count



	# Wrapper method for accessing data structure.
	def __check_file_status(self, api_data: dict, checked_avs: list, detected_count: int) -> tuple[bool, int, list]:
		data = api_data['data']
		finished, detected_count = self.__check_status(data, checked_avs, detected_count)
		return finished, detected_count, data



	# Wrapper method for accessing data structure.
	def __check_url_status(self, api_data: dict, checked_avs: list, detected_count: int) -> tuple[bool, int, list]:
		data = api_data['data']['scanner_results']
		finished, detected_count = self.__check_status(data, checked_avs, detected_count)
		return finished, detected_count, data



	def __wait_complete(self, url: str, target_method: callable, http_method: str) -> Union[None, str]:
		count = 6
		checked_avs = []
		detected_count = 0
		response_text = None
		data = []
		scan_start_time = datetime.utcnow()
		result_requests = {
			'GET': self.ks_http.get_req,
			'POST': self.ks_http.post_req
		}
		result_request = result_requests.get(http_method)
		self.logger.info(f'{INFO_NOTIF} Press CTRL+C to terminate the scanning process at any point and save results to stdout and an outfile provided.')
		try:
			# Scan loop.
			while True:
				# Send get request to KS API and parse API JSON data.
				response_text = result_request(url)
				api_data = json.loads(response_text)

				# Call target scanning method, for data extraction.
				finished, detected_count, data = target_method(api_data, checked_avs, detected_count)

				# Check time in minutes, if equal to or greater than max minutes break the loop.
				time_difference = datetime.utcnow() - scan_start_time
				if finished or (time_difference.seconds >= self.max_minutes * 60) or (len(checked_avs) >= len(data)-MAX_REMAINING_AVS):
					break

				# Delay execution.
				count = self.__sleep_count(count)

		# Stop scanning via CTRL+C.
		except KeyboardInterrupt:
			pass

		# Notify the user of unfinished antivirus engines.
		self.logger.info(f'{INFO_NOTIF} Unfinished AV engines:')
		for av_dict in data:
			av_name = av_dict['avname']
			if av_name not in checked_avs:
				self.logger.info(f'\t - {av_name} (status: {av_dict["status"]})')
		
		self.logger.info(f'Detection ratio: {detected_count} / {len(checked_avs)}')
		return response_text



	def __handle_output(self, result: dict, output_format: Union[None, str], out_file: Union[None, str]) -> str:
		# Format the result.
		result = format_result(output_format, result)

		# Handle out_file.
		self.__handle_out_file(out_file, result)

		# Return formatted result.
		return result



	def __finish_scan(self, url: str, target_method: callable, output_format: Union[None, str], out_file: Union[None, str], http_method: Optional[str]='GET') -> str:
		# Wait for scan to complete.
		result = self.__wait_complete(url, target_method, http_method)

		# Return formatted result.
		return self.__handle_output(result, output_format, out_file)



	@check_types
	def scan(self, file: str, av_list: Optional[list[str]]=None, output_format: Optional[str]=None, out_file: Optional[str]=None) -> str:
		if not file_is_32mb(file):
			raise KsFileTooLargeError

		# Default result is JSON, get JSON to eliminate redundancy.
		file_data = read_file(file)
		if not file_data:
			raise KsFileEmptyError

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Beginning scan token extraction process on file "{file}", be patient this may take some time...')

		# Post the scan request.
		api_data = self.ks_http.post_scan('https://kleenscan.com/api/v1/file/scan',
			files={'path': file_data},
			data={'avList': ','.join(av_list) if av_list else 'all'}
		)

		# Temporary token.
		scan_token = api_data['data']['scan_token']

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Extracted scan token {scan_token} for scan on file "{file}". File scanning process will begin, this will take some time, be patient..')

		# Return formatted result.
		return self.__finish_scan(f'https://kleenscan.com/api/v1/file/result/{scan_token}',
			self.__check_file_status,
			output_format,
			out_file
		)



	@check_types
	def scan_runtime(self, file: str, av_list: Optional[list[str]]=None, output_format: Optional[str]=None, out_file: Optional[str]=None, connect: Optional[bool]=False) -> str:
		if not file_is_32mb(file):
			raise KsFileTooLargeError

		# Default result is JSON, get JSON to eliminate redundancy.
		file_data = read_file(file)
		if not file_data:
			raise KsFileEmptyError

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Beginning scan token extraction process on file "{file}", be patient this may take some time...')

		# Post the scan request.
		api_data = self.ks_http.post_scan('https://kleenscan.com/api/v1/runtime/scan',
			files={'path': file_data},
			data={'avList': ','.join(av_list) if av_list else 'all', 'connect_internet': connect}
		)

		# Temporary token.
		scan_token = api_data['data']['scan_token']

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Extracted scan token {scan_token} for scan on file "{file}". File scanning process will begin, this will take some time, be patient..')

		# Await scan/user to be available in the queue.
		self.logger.info(f'{INFO_NOTIF} Awaing runtime scanning queue slot to be available, be patient..')
		while True:
			data = self.ks_http.get_req_json(f'https://kleenscan.com/api/v1/runtime/status/{scan_token}')
			if data['status'] == 3:
				break
			sleep(1)

		# Return formatted result.
		return self.__finish_scan(f'https://kleenscan.com/api/v1/runtime/result/{scan_token}',
			self.__check_file_status,
			output_format,
			out_file,
			'POST'
		)



	@check_types
	def scan_url(self, url: str, av_list: Optional[list[str]]=None, output_format: Optional[str]=None, out_file: Optional[str]=None) -> str:
		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Beginning route token extraction process on url "{url}", be patient this may take some time...')

		# Default result is JSON, get JSON to eliminate redundancy.
		api_data = self.ks_http.post_scan('https://kleenscan.com/api/v1/url/scan',
			data={
				'avList': ','.join(av_list) if av_list else 'all',
				'url': url
			}
		)

		# Get temporary url token.
		tmp_token = api_data['data']

		# Get route token.
		route_token = self.__get_url_route_token(f'https://kleenscan.com/api/v1/url/status/{tmp_token}')

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Extracted route token {route_token} for scan on url "{url}". URL scanning process will begin, this will take some time, be patient..')

		# Return formatted result.
		return self.__finish_scan(f'https://kleenscan.com/api/v1/url/result/{route_token}',
			self.__check_url_status,
			output_format,
			out_file
		)



	@check_types
	def scan_urlfile(self, url: str, av_list: Optional[list[str]]=None, output_format: Optional[str]=None, out_file: Optional[str]=None) -> str:
		# Download file into memory.
		self.logger.info(f'{INFO_NOTIF} Downloding remote file hosted on server "{url}" into memory/RAM, be patient this may take some time...')
		file_data = self.ks_http.download_file_memory(url)


		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Beginning scan token extraction process on remote file hosted on server "{url}", be patient this may take some time...')

		# Post the scan request.
		api_data = self.ks_http.post_scan('https://kleenscan.com/api/v1/file/scan',
			files={'path': file_data},
			data={'avList': ','.join(av_list) if av_list else 'all'}
		)

		# Temporary token.
		scan_token = api_data['data']['scan_token']

		# Notify the user.
		self.logger.info(f'{INFO_NOTIF} Extracted scan token {scan_token} for scan on file hosted on server "{url}". File scanning process will begin, this will take some time, be patient..')

		# Return formatted result.
		return self.__finish_scan(f'https://kleenscan.com/api/v1/file/result/{scan_token}',
			self.__check_file_status,
			output_format,
			out_file
		)



	@check_types
	def av_list(self, output_format: Optional[str]=None, out_file: Optional[str]=None) -> str:
		result = self.ks_http.get_req('https://kleenscan.com/api/v1/get/avlist')
		api_data = json.loads(result)

		# Notify the user.
		if self.verbose:
			for av_id, av_list in api_data['data'].items():
				self.logger.info(f'{SUCCESS_NOTIF} {av_id}')
				for av_name in av_list:
					self.logger.info(f'\t - {av_name}')

		# Finally return result regardless.
		return self.__handle_output(result, output_format, out_file)


