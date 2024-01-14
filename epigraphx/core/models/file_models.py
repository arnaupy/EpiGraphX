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
import os
from pydantic import BaseModel, model_validator
from typing import ClassVar

from ...databases import files_system

            
class InvalidFileExtension(Exception):
    """Raises when the file name missmatches the class extention"""  
    
class FileNotFound(Exception):
    """Raises when file can't be found"""  
      
    
class FileBaseMeta(type(BaseModel)):
    def __new__(cls, name, bases, namespace, **kwargs):
        # Check if it's the FileBase class itself
        if name == "FileBase":
            return super().__new__(cls, name, bases, namespace, **kwargs)

        # Check if the subclass has 'directory' and 'extensions' attributes
        if "directory" not in namespace or "extensions" not in namespace:
            raise TypeError(f"{name} must have 'directory' and 'extensions' attributes.")

        return super().__new__(cls, name, bases, namespace, **kwargs)

class FileBase(BaseModel, metaclass = FileBaseMeta):
    """Raw file class to mount different file extentions"""
    
    filename: str
    
    @classmethod
    def get_filepath(cls, filename: str) -> str:
        return os.path.join(cls.directory, filename)
    
    @property
    def filepath(self) -> str:
        return os.path.join(self.directory, self.filename)
    
    def _exists(self) -> bool:
        return os.path.isfile(self.filepath)

    
    @model_validator(mode = "after")
    def filename_matches_extensions_and_exists(self):

        filename_extension = self.filename.split(".")[-1]
        if filename_extension not in self.extensions:
            raise InvalidFileExtension(f"'{self.__class__.__name__}' only accepts file extensions in {self.extensions}")
        
        if not self._exists():
            raise FileNotFound(f"'{self.filename}' is not stored in the system")
    
    
class NetworkFile(FileBase):
    """Network file class"""
    
    directory: ClassVar[str] = files_system.NETWORK_FILE["directory"]
    extensions: ClassVar[list[str]] = files_system.NETWORK_FILE["extensions"]