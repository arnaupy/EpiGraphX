"""
Process files in the system:

    NAME -> file_processors.py

    DESCRIPTION -> This file deals with any file process in the app
    
    CLASSES: 
    |
    |   * FileProcessor -> Base class to process files
    |
    |
    |   * UploadFileProcessor(FileProcessor, ABC) -> Abstract class to process `create` & `pull` & `delete` functionalities
    |
    |       methods:
    |           - delete -> deletes a file from the system
    |           
    |               inputs: 
    |                   - self
    |                   - file(FileBase): text file instance
    |                   
    |               outputs -> (bool): Returns true if file was succesfully deleted
    |
    |
    |   * UploadTextFileProcessor(UploadFileProcessor) -> Deals with text files uploaded from a local machine
    |       
    |       methods:
    |           - store -> read the file text content and writes it in a `.txt` file
    |           
    |               inputs: 
    |                   - directory(Dirnames): directory name where the file is stored
    |                   - file(UploadFile): FastAPI file object uploaded 
    |                   
    |               outputs -> (dict): `stored file name` and `size`
    |
    |           - pull -> pull the file form the system if exists.
    |           
    |               inputs: 
    |                   - self
    |                   - directory(Directories): directory where the file is stored
    |                   - filename(str): filename with extension included
    |                   
    |               outputs -> (TextFile): `TextFile` instance | (None): If file doesn't exist
    |
    |           + UploadTextProcessor methods
    +
    
    FUNCTIONS:
    |
    |   * get_file_processor -> get a `FileProcessor` subclass instance
    |
    |       inputs:
    |           - extension(<str>=FileExtensions): File extension. *Error is raised if the input is not i FileExtensions*
    |           - uploaded(bool): True -> uploaded from a local machine | False -> `TODO` 
    |        
    |       outputs -> (FileProcessor)
    |
    |
    |   * get_files -> walk to every app file returning filenames fo every directory leave
    |
    |       outputs -> (dict[str, list[str]])
    |
    +
"""
import os
from fastapi import UploadFile
from typing import Union, Type
import shutil

from ...config import system
from ..models.file_models import NetworkFile
from ...databases import files_system

FileClass = Type[NetworkFile]
StoredFile = NetworkFile
    

class FileProcessor:
    """Base file processor class"""


class UploadFileProcessor(FileProcessor):
    """File processor for local uploads to deal with storing, pulling and deleating functionalities"""
    
    def __init__(self, file_class: FileClass) -> None:
        self.file_class = file_class
        
    def store(self, uploaded_file: UploadFile) -> dict[str, int]:
        
        save_path = self.file_class.get_filepath(uploaded_file.filename)
        with open(save_path, "wb") as dest_file:
            shutil.copyfileobj(uploaded_file.file, dest_file)
            
        return {"filename": uploaded_file.filename, "size": uploaded_file.size}
    
    def pull(self, filename: str) -> StoredFile | None:

        try:
            return self.file_class(filename = filename)
        except:
            return None
        
    def delete(self, file: StoredFile) -> bool:
        
        os.remove(file.filepath)
        return True
    
    
class RequestFileProcessor(FileProcessor):
    pass
    
    
Processor = Union[UploadFileProcessor, RequestFileProcessor]
def get_file_processor(uploaded: bool, file_class: FileClass) -> Processor:
    """Returns an instance of the correponding file processor"""
    
    if not uploaded:
        raise NotImplementedError
    
    return UploadFileProcessor(file_class)
    
    
def get_files() -> dict[str,list[str]]:
    """Returns all the files in the diferent directories"""
    
    return {dirpath: filenames for dirpath, _, filenames in os.walk(files_system.ROOT)}
 

        
        
        
        
        