from . import file_config

# File system variables
ROOT, DIRECTORIES = file_config.read_directories_from_yaml()

# Time format to store in database
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMEDELTA_FORMAT = "%H:%M:%S"

# Default database id lenght
DATABASE_ID_LENGHT = 30