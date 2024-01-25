"""
TODO

    NAME -> file_models.py

    DESCRIPTION -> TODO
"""
import os
from pydantic import BaseModel
from minio import Minio
from typing import ClassVar


class FileBaseMeta(type(BaseModel)):
    def __new__(cls, name, bases, namespace, **kwargs):
        # Check if it's the FileBase class itself
        if name == "FileBase":
            return super().__new__(cls, name, bases, namespace, **kwargs)

        # Check if the subclass has 'directory' and 'extensions' attributes
        if "directory" not in namespace or "extensions" not in namespace:
            raise TypeError(
                f"{name} must have 'directory' and 'extensions' attributes."
            )

        return super().__new__(cls, name, bases, namespace, **kwargs)


class FileBase(BaseModel, metaclass=FileBaseMeta):
    """Raw file class to mount different file extentions"""

    filename: str
    file: bytes

    @classmethod
    def get_filepath(cls, filename: str) -> str:
        return os.path.join(cls.directory, filename)

    @property
    def filepath(self) -> str:
        return os.path.join(self.directory, self.filename)

    def _exists(self) -> bool:
        return os.path.isfile(self.filepath)

    @classmethod
    def create_all(cls, minio_client: Minio, bucket_name: str) -> None:
        # Create the root bucket if not exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)


class NetworkFile(FileBase):
    """Network file class"""

    directory: ClassVar[str] = "networks"
    extensions: ClassVar[list[str]] = [".txt", ".edges", ".csv"]
