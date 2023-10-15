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
from fastapi import UploadFile
from abc import ABC, abstractmethod
import os

from ...config import config
from ..utils.file_utils import get_path
from ..models.file_models import (
    Dirnames, 
    FileExtensions, 
    FileBase, 
    TextFile, 
    NetworkFile
    )


class FileProcessor:
    """Base file processor class"""


class UploadFileProcessor(FileProcessor, ABC):
    """File processor for local uploads to deal with storing, pulling and deleating functionalities"""
    
    @abstractmethod
    def store(self, file: UploadFile, dirname: Dirnames) -> dict[str, any]:
        """Stores a file into the system"""
        
    @abstractmethod
    def pull(self, filename: str, dirname: Dirnames) -> FileBase:
        """Pull the file by filename from system files according to the directory"""
        
    def delete(self, file: FileBase) -> bool:
        """Delete the file"""
        
        os.remove(file.path)
        return True
        
        
class UploadTextFileProcessor(UploadFileProcessor):
    """Text file processor for files locally uploaded"""
    
    def store(self, file: UploadFile, dirname: Dirnames) -> dict[str, any]:
        
        save_path = get_path(config.DIRECTORIES[dirname], file.filename)
        with open(save_path, "wb") as text_file:
            text_file.write(file.file.read())
            
        return {"filename": file.filename, "size": file.size}
    
    def pull(self, filename: str, dirname: Dirnames) -> TextFile:
        
        TEXT_FILES = {
            Dirnames.NETWORKS: NetworkFile
        }
 
        try:
            return TEXT_FILES[Dirnames.get(dirname)](name = filename)
        except:
            return None
    
    
def get_file_processor(extension: FileExtensions, uploaded: bool) -> FileProcessor:
    """Returns an instance of the correponding file processor"""
    
    if not uploaded:
        raise NotImplementedError
    
    PROCESSORS = {
        FileExtensions.TXT: {
            True: UploadTextFileProcessor()
        }
    }
    
    return PROCESSORS[FileExtensions.get(extension)][uploaded]
    
    
def get_files() -> dict[str,list[str]]:
    """Returns all the files in the diferent directories"""
    
    return {dirpath: filenames for dirpath, _, filenames in os.walk(config.ROOT)}
 

        
        
        
        
        