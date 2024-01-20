import sys
import logging

from .config.__logger import FORMAT, DATEFMT, LOGS_FILENAME


# Create logger object
logger = logging.getLogger()

# Create formater
formatter = logging.Formatter(FORMAT, datefmt=DATEFMT)

# Create handlers
file_handler = logging.FileHandler(filename=LOGS_FILENAME)
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
