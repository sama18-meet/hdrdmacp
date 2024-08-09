# utils.py

import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message):
    """Log a message to the console."""
    logging.info(message)

def read_file(file_path, chunk_size):
    """Generator to read a file in chunks."""
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            yield chunk

def write_file(file_path, data, mode='wb'):
    """Write data to a file."""
    with open(file_path, mode) as file:
        file.write(data)

def file_exists(file_path):
    """Check if a file exists."""
    return os.path.isfile(file_path)

def get_file_size(file_path):
    """Get the size of a file."""
    return os.path.getsize(file_path)
