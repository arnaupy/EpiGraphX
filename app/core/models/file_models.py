"""
File classes:

    NAME -> file_models.py

    DESCRIPTION -> TODO
    
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
    +
"""
from pydantic import BaseModel, model_validator
from enum import Enum
import os

from ...config import config
from ..utils import file_utils

class FileExtensions(Enum):
    TXT = ".txt"

    @classmethod
    def get(cls, value: str):
        for extension in cls:
            if extension.value == value:
                return extension

class Dirnames(Enum):
    NETWORKS = "networks"

    @classmethod
    def get(cls, value: str):
        for extension in cls:
            if extension.value == value:
                return extension
            
            
class InvalidFileExtension(Exception):
    """Raises when the file name missmatches the class extention"""  
    
class FileNotFound(Exception):
    """Raises when file can't be found"""  
      

class FileBase(BaseModel):
    """Raw file class to mount different file extentions"""
    
    name: str
    directory: str = config.ROOT
    
    @model_validator(mode = "after")
    def name_match_extension_and_exists(cls, values):
        """Check that the file name extension matches extension class attribute and exists"""
        
        if values.name[-len(values.extension.value):] != values.extension.value:
            raise InvalidFileExtension(f"File provided should be a `{values.extension.value}` extension.")
    
        file_path = file_utils.get_path(values.directory, values.name)
        if not os.path.isfile(file_path):
            raise FileNotFound(f"File {file_path} is not stored in the system")
        
        return values
    
    @property
    def path(self) -> str:
        """Get full path from base directory"""
        
        return file_utils.get_path(self.directory, self.name)
    
class TextFile(FileBase):
    """Text file class"""
    
    extension: FileExtensions = FileExtensions.TXT
    directory: str = config.ROOT
    
class NetworkFile(TextFile):
    """Network file class"""
    
    directory: str = config.DIRECTORIES[Dirnames.NETWORKS.value]