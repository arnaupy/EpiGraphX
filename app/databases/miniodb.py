"""
Minio database:

    NAME -> miniodb.py

    DESCRIPTION -> This file implements a database connection using 'Minio'.
"""
from functools import lru_cache
from minio import Minio
from pydantic import BaseModel

from app.config import minio_settings

# Initialize Minio client
minio_client = Minio(
    f"{minio_settings.minio_host}:{minio_settings.minio_port}",
    access_key=minio_settings.minio_access_key,
    secret_key=minio_settings.minio_secret_key,
    secure=False,
)

# Set the bucket name
bucket_name = minio_settings.minio_bucket_name


class MinioSession(BaseModel):
    minio_client: Minio
    bucket_name: str

    class Config:
        arbitrary_types_allowed = True


@lru_cache
def get_minio_db():
    return MinioSession(minio_client=minio_client, bucket_name=bucket_name)
