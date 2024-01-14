"""
Process FastAPI responses as schemas to SQLAlchemy database objects:

    NAME -> schemas.py

    DESCRIPTION -> TODO
        
    CLASSES: TODO
    |       
    +
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
import validators


class InvalidStringFormat(Exception):
    """Raises when the string format of the mapped type variable is not correct"""
    
class SizeMissmatchError(Exception):
    """Raises when the size of the array missmatches the array length"""    
    
class NetworkOriginError(Exception):
    """Raises when the origin of a network is incorrect"""
     
    
class OneDimensionalArrayBase(BaseModel):
    """Base class for every SQL database table this stores arrays"""   
    
    array: str
    dtype: str
    size: int    
        
    @field_validator("array")
    @classmethod
    def array_is_valid(cls, value):
        """Validates that the array attribute is an `list string`"""
        
        assert type(eval(value)) == list, InvalidStringFormat("`array` attribute must be a 'list string'.")
        return value
    
    @field_validator("size")
    @classmethod
    def size_is_valid(cls, value, values):
        """Validates that the size is a `tuple string`."""

        decoded_array = eval(values.data["array"])
        
        assert len(decoded_array) == value, SizeMissmatchError(
            f"`size` attribute don't match array lenght : ({value},{decoded_array.size})")

        return value

        
class DegreeBase(OneDimensionalArrayBase):
    """Base class for `Degree` table"""
    network_id: str

class Degree(DegreeBase):
    """Degree database mapping"""
    id: str

    class ConfigDict:
        from_attributes = True
              
        
class LinkBase(OneDimensionalArrayBase):
    """Base class for `Link` table"""
    network_id: str

class Link(LinkBase):
    """Link database mapping"""
    id: str

    class ConfigDict:
        from_attributes = True
            

class PiniBase(OneDimensionalArrayBase):
    """Base class for `Pini` table"""
    network_id: str

class Pini(PiniBase):
    """Pini database mapping"""
    id: str

    class ConfigDict:
        from_attributes = True
        
        
class PfinBase(OneDimensionalArrayBase):
    """Base class for `Pfin` table"""
    network_id: str

class Pfin(PfinBase):
    """Pfin database mapping"""
    id: str

    class ConfigDict:
        from_attributes = True


class NetworkBase(BaseModel):
    """Network class for `Network` table"""
    label: str 
    origin: str
    is_private: bool = True
    
    @classmethod
    def _is_private(cls, origin):
        if validators.url(origin):
            return False
    
        else:
            return True
        
    
    @field_validator("origin")
    @classmethod
    def origin_is_url_or_filepath(cls, value):
        """
        Validates that whether the network was updated by the client
        or requested from a network data repository, its format is correct
        """
        
        origin = value
   
        if cls._is_private(origin) == None:
            raise NetworkOriginError(f"Origin must be a valid `url` or a file")
    
        return origin
        
    
    @field_validator("is_private")
    @classmethod
    def assign_id_private(cls, value, values):
        return cls._is_private(values.data.get("origin"))
        

    class ConfigDict:
        from_attributes = True
        validate_assignment = True
    

class NetworkCreate(NetworkBase):
    """Network class used when creating a network"""

class NetworkUpdate(NetworkBase):
    """Network class to update the accessible attributes"""
    label: str | None = None
    origin: str | None = None

class NetworkSummary(NetworkBase):
    """Network class used to show the short storage attrbutes of a network"""
    
    id: str
    nodes: int | None = None
    edges: int | None = None
    is_scanned: bool | None
    last_update: datetime
    last_scan: datetime | None = None
    time_to_scan: str | None = None

class Network(NetworkSummary):
    """Network database mapping"""
    degree: Degree | None = None
    link: Link | None = None
    pini: Pini | None = None
    pfin: Pfin | None = None

    # class ConfigDict:
    #     from_attributes = True
        
    