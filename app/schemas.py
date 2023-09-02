from pydantic import BaseModel
from typing import Optional
        
        
class DegreeBase(BaseModel):
    network_id: str
    item_position: int
    item_value: int


class DegreeCreate(DegreeBase):
    pass


class Degree(DegreeBase):
    id: str

    class Config:
        orm_mode = True
        
        
class LinkBase(BaseModel):
    network_id: str
    item_position: int
    item_value: int


class LinkCreate(LinkBase):
    pass


class Link(LinkBase):
    id: str

    class Config:
        orm_mode = True
        

class PiniBase(BaseModel):
    network_id: str
    item_position: int
    item_value: int


class PiniCreate(PiniBase):
    pass


class Pini(PiniBase):
    id: str

    class Config:
        orm_mode = True
        
        
class PfinBase(BaseModel):
    network_id: str
    item_position: int
    item_value: int


class PfinCreate(PfinBase):
    pass


class Pfin(PfinBase):
    id: str

    class Config:
        orm_mode = True


class NetworkBase(BaseModel):
    label: str
    file_path: str
    nodes: Optional[int]
    edges: Optional[int]


class NetworkCreate(NetworkBase):
    pass


class Network(NetworkBase):
    id: str
    is_read: bool
    degree: list[Degree] = []
    link: list[Link] = []
    pini: list[Pini] = []
    pfin: list[Pfin] = []

    class Config:
        orm_mode = True