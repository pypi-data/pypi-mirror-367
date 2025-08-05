import argparse
import sys

# Custom library imports:
from .kleenscan import Kleenscan
from .lib.config import *
from .lib.errors import *



def cli_run(args: argparse.ArgumentParser) -> None:
	# --silent/-s
	verbose = not args.silent

	# Instantiate kleenscan object.
	ks = Kleenscan(args.token, verbose, args.mins)

	# --file/-f
	if args.file:
		result = ks.scan(args.file, args.antiviruses, args.format, args.outfile)

	# --runtime/-r
	if args.runtime:
		result = ks.scan_runtime(args.runtime, args.antiviruses, args.format, args.outfile)

	# --url/-u
	elif args.url:
		result = ks.scan_url(args.url, args.antiviruses, args.format, args.outfile)

	# --list/-l
	elif args.list:
		result = ks.av_list(args.format, args.outfile)

	# --remotefile/-rf
	elif args.urlfile:
		result = ks.scan_urlfile(args.urlfile, args.antiviruses, args.format, args.outfile, args.connect)

	# --show/-sh
	if args.show:
		print(result)



def main():
	parser = argparse.ArgumentParser(description=CLI_DESCRIPTION,
		epilog=CLI_EPILOG
	)

	# Mutally exclusive arguments.
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--file', '-f', type=str, help='scan a file using Kleenscan')
	group.add_argument('--runtime', '-r', type=str, help='scan a file using Kleenscan runtime scanning/dynamic analysis')
	group.add_argument('--urlfile', '-uf', type=str, help='Download a remote file hosted on a HTTP server into memory and upload/scan the file from memory on Kleenscan (e.g.: -uf https://malicious.com/file.exe). This approach never touches disk')
	group.add_argument('--url', '-u', type=str, help='scan a URL using Kleenscan')
	group.add_argument('--list', '-l', action='store_true', help='list available anti-virus vendors on Kleenscan')

	# Optional arguments.
	parser.add_argument('--antiviruses', '-avs', type=str, nargs='+', help='user-provided list of anti-virus to scan the file set with --file/-f. You can view available AV vendors using the --list/-l flag (default is "all" for all anti-virus vendors). Example "-avs avg avast microsoftdefender"')
	parser.add_argument('--format', '-of', type=str, default='json', choices=['json', 'toml', 'yaml'], help='select output format type, available types are: json, toml, yaml (default is json)')
	parser.add_argument('--outfile', '-o', type=str, help='output file to store results on disk (not required and can be omitted)')
	parser.add_argument('--silent', '-s', action='store_true', help='Verbose mode, only the scanner result outout will be outputted upon being finished')
	parser.add_argument('--connect', '-c', action='store_true', help='Connect scanner VMs to the internet.')
	parser.add_argument('--mins', '-m', type=int, default=MAX_SCAN_TIME, help=f'Max scan time in minutes to discontinue the scan process default is {MAX_SCAN_TIME}')
	parser.add_argument('--show', '-sh', action='store_true', help=f'Show Kleenscan output to be outputted to a file, set with the --format/-of parameter')

	# Required arguments.
	parser.add_argument('--token', '-t', type=str, required=True, help='API token generated at https://kleenscan.com/profile. It is required to use this application')

	# If no args show help command.
	if len(sys.argv) == 1:
		parser.print_help(sys.stderr)
	
	else:
		# Parse arguments.
		args = parser.parse_args()
		try:
			cli_run(args)
		except (KsApiError,
			KsFileEmptyError,
			KsFileTooLargeError,
			KsRemoteFileTooLargeError,
			KsGetFileInfoFailedError,
			KsNoFileHostedError,
			KsFileDownloadFailedError,
			KsDeadLinkError,
			KsHttpError
		) as e:
			sys.exit(f'[ERROR] {e}')

		except FileNotFoundError:
			sys.exit(f'[ERROR] File "{args.file}" not found for scanning.')

		except PermissionError:
			sys.exit(f'[ERROR] Invalid permissions for file: "{args.file}".')


if __name__ == '__main__':
    main()