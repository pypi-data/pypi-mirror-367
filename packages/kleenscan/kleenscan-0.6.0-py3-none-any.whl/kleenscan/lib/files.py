import os



# Custom library imports:
from .config import *



def file_is_32mb(filename: str) -> bool:
    file_size = os.path.getsize(filename)
    return file_size <= (MAX_FILE_MB * 1024 * 1024)



def read_file(filename: str) -> bytes:
    with open(filename, 'rb') as f:
        return f.read()



def write_file(filename: str, data: str) -> None:
	with open(filename, 'w') as f:
		f.write(data)
