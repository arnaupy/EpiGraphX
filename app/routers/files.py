"""
TODO

    NAME -> files.py

    DESCRIPTION -> TODO
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.core.features import crud_files
from app.core.models import file_models
from app.config import Tags

from app.databases.miniodb import MinioSession, get_minio_db


router = APIRouter(prefix="/files", tags=[Tags.FILES])


@router.get("/")
async def get_filenames(minio_db: MinioSession = Depends(get_minio_db)):
    """Get a summary of all the files and directories in files system path"""

    return crud_files.get_filenames(minio_db)


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
    processor = crud_files.get_file_processor(
        uploaded=True, file_class=file_models.NetworkFile, minio_db=minio_db
    )

    # Validate that the file extension is valid
    if not processor.validate_file_extension(file):
        raise HTTPException(
            status_code=400,
            detail=f"Network files only accepts file extensions in {file_models.NetworkFile.extensions}",
        )

    # Checks that the file is not already uploaded
    network_file = processor.pull(filename=file.filename)
    if network_file:
        raise HTTPException(status_code=400, detail="The file is already uploaded")

    # Stores the file in the system
    return {"uploaded_file": processor.store(uploaded_file=file)}


@router.get("/networks")
async def download_network_file(
    filename: str, minio_db: MinioSession = Depends(get_minio_db)
):
    """Download a file from the system given a file path"""

    # Instanciate file processor
    processor = crud_files.get_file_processor(
        uploaded=True, file_class=file_models.NetworkFile, minio_db=minio_db
    )

    # Check that the file is stored in the system
    network_file = processor.pull(filename=filename)
    if not network_file:
        raise HTTPException(status_code=400, detail="File not found")

    # Download the network
    return processor.download(file=network_file)


@router.delete("/networks")
async def delete_network_file(
    filename: str, minio_db: MinioSession = Depends(get_minio_db)
):
    """Deletes a file from the system given a file path"""

    # Instanciate file processor
    processor = crud_files.get_file_processor(
        uploaded=True, file_class=file_models.NetworkFile, minio_db=minio_db
    )

    # Check that the file is stored in the system
    network_file = processor.pull(filename=filename)
    if not network_file:
        raise HTTPException(status_code=400, detail="File not found")

    # Deletes the network
    return {"deleted": processor.delete(file=network_file)}
