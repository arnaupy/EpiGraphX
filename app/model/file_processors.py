"""
Process files in the system:

    NAME -> file_processors.py

    DESCRIPTION -> This file deals with any file process in the app
    
    CLASSES: 
    |
    |   * FileExtension -> Enums file extensions
    |       
    |       attributes: 
    |           - TXT(str) = ".txt": text file extention 
    |
    |       methodes: 
    |           - get(@classmethod) -> get the corresponding attribute by its value
    |
    |               inputs:
    |                   - value(str): class value 
    |                
    |               outputs -> (Directories): class attribute 
    |                
    |               ex -> in: value = ".txt" | out: Directories.TXT
    |
    |
    |   * Directories -> Enums system file directories
    |       
    |       attributes: 
    |           - DEAFULT(None) = None: default directory to store files is the root
    |           - NETWORK(str) = "networks": directory to store network files
    |
    |       methodes: 
    |           + FileExtension method
    |
    |
    |   * FileBase(BaseModel) -> Pydantic base class for any kind of file
    |
    |       attributes:
    |           - name(str): file name
    |           - directory(Directories) = Directories.DEFAULT: file directory. Default is the root    
    |       
    |       methods:
    |           - name_match_extension_and_exists(@model_validator) -> validates that the `name` provided 
    |                                                                  matches the `extension` and the file exists
    |           - path(@property) -> computes the full file directory from root
    |
    |               inputs: self 
    |                   
    |               outputs -> (str): file path from root
    | 
    |
    |   * TextFile(FileBase) -> Base class for text files with extention `.txt`
    |
    |       attributes:
    |           - extension(FileExtension) = FileExtension.TXT: text file extension
    |           + FileBase attributes
    |
    |       methods:
    |           + FileBase methods
    | 
    |
    |   * NetworkFile(TextFile) -> Network file class
    |
    |       attributes:
    |           - directory(Directories) = Directories.NETWORKS: file directory 
    |           + TextFile attributes
    |
    |       methods:
    |           + TextFile methods
    |
    |
    |   * UploadFileProcessor(ABC) -> Abstract class to process `create` & `pull` & `delete` functionalities
    |
    |       methods:
    |           - delete -> deletes a file from the system
    |           
    |               inputs: 
    |                   - self
    |                   - file(FileBase): text file instance
    |                   
    |               outputs -> (bool): Returns true file was succesfully deleted
    |
    |   * UploadTextFileProcessor(UploadFileProcessor) -> Deals with text files uploaded from a local machine
    |
    |       attributes: None  
    |       
    |       methods:
    |           - store -> read the file text content and writes it in plain file in `.txt` extension
    |           
    |               inputs: 
    |                   - self
    |                   - directory(Directories): directory where the file is stored
    |                   - file(UploadFile): file object uploaded by FastAPI
    |                   
    |               outputs -> (dict): stored file name and size as a dictionary
    |
    |           - pull -> pull the file form the system if exists
    |           
    |               inputs: 
    |                   - self
    |                   - directory(Directories): directory where the file is stored
    |                   - filename(str): filename with extension included
    |                   
    |               outputs -> (TextFile): pull a `TextFile` instance
    |
    |           + UploadTextFile methods
    +
    
    FUNCTIONS:
    |
    |   * _get_path -> get the full file path from root
    |
    |       inputs:
    |           - *args(tuple(str)): tuple of directories and/or file to join
    |        
    |       outputs -> (str): file path including the root
    +
"""
from pydantic import BaseModel, model_validator
from fastapi import UploadFile
from abc import ABC, abstractmethod
from enum import Enum
from glob import glob
import os

DEFAULT_FILE_DIRECTORY = os.environ["DEFAULT_FILE_DIRECTORY"]

class FileExtensions(Enum):
    TXT = ".txt"

    @classmethod
    def get(cls, value: str):
        for extension in cls:
            if extension.value == value:
                return extension
    
class Directories(Enum):
    DEFAULT = None
    NETWORKS = os.environ["DEFAULT_NETWORK_DIRECTORY"]
    
    @classmethod
    def get(cls, value: str):
        for directory in cls:
            if directory.value == value:
                return directory
            
            
class InvalidFileExtension(Exception):
    """Raises when the file name missmatches the class extention"""  
    
class FileNotFound(Exception):
    """Raises when file can't be found"""  
    

def _get_path(*args) -> str:
    """Joins directories and/or a file in a single path"""
    return DEFAULT_FILE_DIRECTORY + "/" + "/".join([arg for arg in args if arg != None])
      

class FileBase(BaseModel):
    """Raw file class to mount different file extentions"""
    
    name: str
    directory: Directories = Directories.DEFAULT
    
    @model_validator(mode = "after")
    def name_match_extension_and_exists(cls, values):
        """Check that the file name extension matches extension class attribute and exists"""
        
        if values.name[-len(values.extension.value):] != values.extension.value:
            raise InvalidFileExtension(f"File provided should be a `{values.extension.value}` extension.")
    
        file_path = _get_path(values.directory.value, values.name)
        if not os.path.isfile(file_path):
            raise FileNotFound(f"File {file_path} is not stored in the system")
        
        return values
    
    @property
    def path(self) -> str:
        """Get full path from base directory"""
        
        return _get_path(self.directory.value, self.name)
    
class TextFile(FileBase):
    """Text file class"""
    
    extension: FileExtensions = FileExtensions.TXT
    
class NetworkFile(TextFile):
    """Network file class"""
    
    directory: Directories = Directories.NETWORKS


class FileProcessor:
    """Base file processor class"""

class UploadFileProcessor(FileProcessor, ABC):
    """File processor for local uploads to deal with storing, pulling and deleating functionalities"""
    
    @abstractmethod
    def store(self, file: UploadFile, directory: Directories) -> dict[str, any]:
        """Stores a file into the system"""
        
    @abstractmethod
    def pull(self, filename: str, directory: Directories) -> FileBase:
        """Pull the file by filename from system files according to the directory"""
        
    def delete(self, file: FileBase) -> bool:
        """Delete the file"""
        
        os.remove(file.path)
        return True
        
class UploadTextFileProcessor(UploadFileProcessor):
    """Text file processor for files locally uploaded"""
    
    def store(self, file: UploadFile, directory: Directories) -> dict[str, any]:
        
        save_path = _get_path(directory, file.filename)
        with open(save_path, "wb") as text_file:
            text_file.write(file.file.read())
            
        return {"filename": file.filename, "size": file.size}
    
    def pull(self, filename: str, directory: Directories) -> TextFile:
        
        TEXT_FILES = {
            Directories.DEFAULT: TextFile,
            Directories.NETWORKS: NetworkFile
        }
        try:
            return TEXT_FILES[Directories.get(directory)](name = filename)
        except:
            return None
    
    
def get_file_processor(extension: FileExtensions, uploaded: bool) -> FileProcessor:
    """Returns an instance of the correponding file processor"""
    
    PROCESSORS = {
        FileExtensions.TXT: {
            True: UploadTextFileProcessor()
        }
    }
    
    return PROCESSORS[FileExtensions.get(extension)][uploaded]
    
 
       
def get_files() -> dict:
    """Returns all the files in the diferent directories"""
    
    files = {}
    for directory in Directories:
        files.update({directory: [os.path.basename(x) for x in glob(_get_path(directory.value, "*.*"))]})
    
    return files

        
        
        
        
        