"""
Manages file system

    NAME -> files.py

    DESCRIPTION -> TODO
       
    FUNCTIONS: TODO
    |
    +
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from ..core.processors import file_processor
from ..core.models import file_models
from ..config.__tags import Tags

from ..databases.miniodb import MinioSession, get_minio_db


router = APIRouter(prefix = "/files", tags=[Tags.FILES])


@router.get("/")
async def get_files(minio_db: MinioSession = Depends(get_minio_db)):
    """Get a summary of all the files and directories in files system path"""

    return file_processor.get_files(minio_db)


@router.post(
    "/networks",
    description=f"""
Uploads a network file into the system.

**File extensions:** {file_models.NetworkFile.extensions}
             """,
)
async def upload_network_file(
    file: UploadFile = File(...), minio_db: MinioSession = Depends(get_minio_db)
):
    # Instanciate file processor
    processor = file_processor.get_file_processor(
        uploaded=True, file_class=file_processor.NetworkFile, minio_db=minio_db
    )

    # Checks that the file is not already uploaded
    network_file = processor.pull(filename=file.filename)
    if network_file:
        raise HTTPException(status_code=400, detail="The file is already uploaded")

    # Stores the file in the system
    return {"uploaded_file": processor.store(uploaded_file=file)}


@router.delete("/networks")
async def delete_network_file(filename: str, minio_db: MinioSession = Depends(get_minio_db)):
    """Deletes a file from the system given a file path"""

    # Instanciate file processor
    processor = file_processor.get_file_processor(
        uploaded=True, file_class=file_processor.NetworkFile, minio_db=minio_db
    )

    # Check that the file is stored in the system
    network_file = processor.pull(filename=filename)
    if not network_file:
        raise HTTPException(status_code=400, detail="File not found")

    # Deletes the network
    return {"deleted": processor.delete(file=network_file)}
