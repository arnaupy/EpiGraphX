import os
import sys
import logging

LOGS_DIRECTORY: str = os.getenv("LOGS_DIRECTORY", "./logs")
BUILD_LOGS_FILENAME: str = "build.log"
FORMAT: str = "%(asctime)s [%(levelname)s]: %(message)s"
DATEFMT: str = "%d-%m-%Y %H:%M:%S"

# Create log file
os.makedirs(LOGS_DIRECTORY, exist_ok = True)

# Create logger object
logger = logging.getLogger()

# Create formater
formatter = logging.Formatter(FORMAT, datefmt = DATEFMT)

# Create handlers
file_handler = logging.FileHandler(filename = os.path.join(LOGS_DIRECTORY, BUILD_LOGS_FILENAME))
stream_handler = logging.StreamHandler(sys.stdout)

# Set formaters
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Set levels 
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)

# Set handlers
logger.handlers = [file_handler, stream_handler]

logger.setLevel(logging.DEBUG)
