# Custom Library imports:
from .cli_colors import *


MAX_REMAINING_AVS = 4
MAX_FILE_MB = 32
MAX_SCAN_TIME = 4

URL_CTEXT = colored(CYAN_COLOR, 'https://kleenscan.com/api_management')
CLI_DESCRIPTION = f'Kleenscan command line interface application. Scan files, urls and list and view available anti-virus, simplified! See {URL_CTEXT} for more information.'


EXAMPLE_CTEXT = colored(YELLOW_COLOR, 'Example')
CLI_EPILOG = f'''
{EXAMPLE_CTEXT}: kleenscan -t <api_token> -f binary.exe --mins 1
'''