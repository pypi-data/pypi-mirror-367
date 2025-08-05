import requests
import json
from typing import *


# Custom Library imports:
from .files import read_file
from .errors import *



class Ks_http:
	def __init__(self, x_auth_token: str):
		self.headers = {'X-Auth-Token': x_auth_token}



	@staticmethod
	def __handle_api_errors(response: requests.Response) -> None:
		if response.status_code != 200:
			raise KsHttpError(response.status_code)

		if "httpResponseCode" in response.text and '"httpResponseCode":200' not in response.text:
			raise KsApiError(response.text)



	def post_scan(self, url: str, data: dict, files: Optional[str]=None) -> dict:
		with requests.post(url,
			headers=self.headers,
			files=files,
			data=data
		) as response:
			self.__handle_api_errors(response)
			# print(response.text)
			return json.loads(response.text)



	def get_req(self, url: str) -> str:
		with requests.get(url,
			headers=self.headers,
		) as response:
			self.__handle_api_errors(response)
			# print(response.text)
			return response.text



	def post_req(self, url: str) -> str:
		with requests.post(url,
			headers=self.headers,
		) as response:
			self.__handle_api_errors(response)
			# print(response.text)
			return response.text



	def get_req_json(self, url: str) -> dict:
		with requests.get(url,
			headers=self.headers,
		) as response:
			self.__handle_api_errors(response)
			return json.loads(response.text)



	def get_req_json_noerr(self, url: str) -> dict:
		with requests.get(url,
			headers=self.headers,
		) as response:
			return json.loads(response.text)



	@staticmethod
	def download_file_memory(url: str) -> bytes:
		try:
			# Send a HEAD request to get the file size.
			with requests.head(url) as response:
				# Check if the request was successful.
				if response.status_code != 200:
					raise KsGetFileInfoFailedError(response.status_code)

				# Get the content type from the headers
				content_type = response.headers.get('Content-Type', '')

	    		# Check if the content type is HTML/text.
				if 'text/html' in content_type:
					raise KsNoFileHostedError
	    
				# Get the file size in MB from the Content-Length header.
				file_size_mb = int(response.headers.get('Content-Length', 0)) / 1024 / 1024

				# Check if the file size in MB exceeds the KS max size in MB.
				if file_size_mb >= MAX_FILE_MB:
					raise KsRemoteFileTooLargeError

				# Send a GET request to download the file.
				with requests.get(url, stream=True) as response:

					# Check if the request was successful.
					if response.status_code != 200:
						raise KsFileDownloadFailedError(response.status_code)

					# Return file content.
					return response.content

			return b''
		except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
			raise KsDeadLinkError(f'{e} caused by {type(e)}')



