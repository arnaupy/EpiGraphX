import os
from minio import Minio
from pydantic import BaseModel

MINIO_HOST = os.environ["MINIO_HOST"]
MINIO_PORT = os.environ["MINIO_PORT"]
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]
MINIO_BUCKET_NAME = os.environ["MINIO_BUCKET_NAME"]

# Initialize Minio client
minio_client = Minio(
    ":".join([MINIO_HOST, MINIO_PORT]),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


class MinioSession(BaseModel):
    minio_client: Minio
    bucket_name: str

    class Config:
        arbitrary_types_allowed = True


def get_minio_db():
    return MinioSession(minio_client=minio_client, bucket_name=MINIO_BUCKET_NAME)
