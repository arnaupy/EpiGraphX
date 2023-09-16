from pydantic import BaseModel
from typing import Optional
        
        
class DegreeBase(BaseModel):
    network_id: str
    position: int
    value: int

class DegreeCreate(DegreeBase):
    pass

class Degree(DegreeBase):
    id: str

    class ConfigDict:
        from_attributes = True
        
      
        
class LinkBase(BaseModel):
    network_id: str
    position: int
    value: int

class LinkCreate(LinkBase):
    pass

class Link(LinkBase):
    id: str

    class ConfigDict:
        from_attributes = True
      
        

class PiniBase(BaseModel):
    network_id: str
    position: int
    value: int

class PiniCreate(PiniBase):
    pass

class Pini(PiniBase):
    id: str

    class ConfigDict:
        from_attributes = True
        
      
        
class PfinBase(BaseModel):
    network_id: str
    position: int
    value: int

class PfinCreate(PfinBase):
    pass

class Pfin(PfinBase):
    id: str

    class ConfigDict:
        from_attributes = True



class NetworkBase(BaseModel):
    label: str 
    file_path: str

class NetworkCreate(NetworkBase):
    pass

class NetworkUpdate(NetworkBase):
    label: str = "None"
    file_path: str = "None"

class NetworkView(NetworkBase):
    id: str
    nodes: Optional[int]
    edges: Optional[int]
    is_read: bool

class Network(NetworkView):
    degree: list[Degree] = []
    link: list[Link] = []
    pini: list[Pini] = []
    pfin: list[Pfin] = []

    class ConfigDict:
        from_attributes = True
    
