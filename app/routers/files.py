"""
Manages file system

    NAME -> files.py

    DESCRIPTION -> TODO
       
    FUNCTIONS: TODO
    |
    +
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..core.processors import file_processor

router = APIRouter(prefix = "/files", tags = ["Files"])


@router.get("/")
async def get_files():
    """Get a summary of all the files and directories in files system path"""
    
    return file_processor.get_files()

@router.post("/networks")
async def upload_network_file(file: UploadFile = File(...)):
    """Uploads a network file into the system"""
    
    # Instanciate file processor
    processor = file_processor.get_file_processor(extension = ".txt", uploaded = True)
    
    # Checks that the file is not already uploaded
    network_file = processor.pull(dirname = "networks", filename = file.filename)
    if network_file:
        raise HTTPException(status_code = 400, detail = "The file is already uploaded")
    
    # Stores the file in the system
    return {"uploaded_file": processor.store(dirname = "networks", file = file)}
        

@router.delete("/networks")
async def delete_network_file(filename: str):
    """Deletes a file from the system given a file path"""
    
    # Instanciate file processor
    processor = file_processor.get_file_processor(extension = ".txt", uploaded = True)
    
    # Check that the file is stored in the system
    network_file = processor.pull(dirname = "networks", filename = filename)
    if not network_file:
        raise HTTPException(status_code = 400, detail = "File not found")
    
    # Deletes the network
    return {"deleted": processor.delete(file = network_file)}

    
    