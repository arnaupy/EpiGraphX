from pydantic_settings import BaseSettings
from pydantic import EmailStr, HttpUrl
from logging import DEBUG, INFO
from enum import Enum


class Tags(Enum):
    FILES = "Files"
    NETWORKS = "Networks"
    LOGS = "Logs"


class _Metadata(BaseSettings):
    project_name: str
    project_description: str
    author: str
    author_email: EmailStr
    contact_url: HttpUrl
    version: str
    license: str


class _LogsSettings(BaseSettings):
    logs_filename: str = "app.log"
    format: str = "%(asctime)s [%(levelname)s]: %(message)s"
    datafmt: str = "%d-%m-%Y %H:%M:%S"

    file_level: int = DEBUG
    stream_level: int = INFO


class _PostgresSettings(BaseSettings):
    postgres_password: str
    postgres_db_name: str
    postgres_host: str
    postgres_user: str
    postgres_port: int

    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    timedelta_format: str = "%H:%M:%S"


class _MinioSettings(BaseSettings):
    minio_host: str
    minio_port: int
    minio_access_key: str
    minio_secret_key: str

    minio_bucket_name: str


# Settings related with external data for the app
metadata = _Metadata()

# Logging python library requires some settings for print loggings in terminal and/or store them in a file
logs_settings = _LogsSettings()

# Settings related with database connection and certain variable formats
postgres_settings = _PostgresSettings()

# Minio access settings
minio_settings = _MinioSettings()
