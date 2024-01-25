import tempfile
from pathlib import Path
from pydantic import BaseModel
from typing import Type
from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.core.models import file_models
from app.databases.miniodb import MinioSession


class FileProcessor(BaseModel):
    """Base class for processing files in the api"""


class UploadFileProcessor(FileProcessor):
    """Class to process a file uploaded to the api by the user by local machine"""

    file_class: Type[file_models.FileBase]
    minio_db: MinioSession

    def store(self, uploaded_file: UploadFile) -> dict[str, int]:
        save_path = self.file_class.get_filepath(uploaded_file.filename)

        self.minio_db.minio_client.put_object(
            self.minio_db.bucket_name,
            save_path,
            uploaded_file.file,
            length=uploaded_file.size,
        )

        return {"filename": uploaded_file.filename, "size": uploaded_file.size}

    def pull(self, filename: str) -> file_models.FileBase:
        try:
            result = self.minio_db.minio_client.get_object(
                self.minio_db.bucket_name, self.file_class.get_filepath(filename)
            )
            return self.file_class(filename=filename, file=result.read())
        except:
            return None

    def delete(self, file: file_models.FileBase) -> bool:
        self.minio_db.minio_client.remove_object(
            self.minio_db.bucket_name, file.filepath
        )
        return True

    def download(self, file: file_models.FileBase) -> FileResponse:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.file)

        return FileResponse(
            temp_file.name,
            media_type="application/octet-stream",
            filename=file.filename,
        )

    def validate_file_extension(self, uploaded_file: UploadFile) -> bool:
        return (
            True
            if Path(uploaded_file.filename).suffix in self.file_class.extensions
            else False
        )


def get_file_processor(
    uploaded: bool, file_class: Type[file_models.FileBase], minio_db: MinioSession
) -> FileProcessor:
    """Returns an instance of the correponding file processor"""

    if uploaded:
        return UploadFileProcessor(file_class=file_class, minio_db=minio_db)

    raise NotImplementedError


def get_filenames(minio_db: MinioSession) -> list:
    """Returns all the files in the diferent directories"""

    objects = minio_db.minio_client.list_objects(minio_db.bucket_name, recursive=True)
    return [obj.object_name for obj in objects]
