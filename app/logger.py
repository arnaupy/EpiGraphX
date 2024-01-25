import sys
import logging

from app.config import logs_settings


# Create logger object
logger = logging.getLogger()

# Create formater
formatter = logging.Formatter(logs_settings.format, datefmt=logs_settings.datafmt)

# Create handlers
file_handler = logging.FileHandler(filename=logs_settings.logs_filename)
stream_handler = logging.StreamHandler(sys.stdout)

# Set formaters
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Set levels
file_handler.setLevel(logs_settings.file_level)
stream_handler.setLevel(logs_settings.stream_level)

# Set handlers
logger.handlers = [file_handler, stream_handler]

logger.setLevel(logging.DEBUG)
