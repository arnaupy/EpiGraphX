from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Network(Base):
    __tablename__ = "network"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    label: Mapped[str]
    file_path: Mapped[str] 
    nodes: Mapped[Optional[int]] 
    edges: Mapped[Optional[int]] 
    is_read: Mapped[bool] = mapped_column(default = False)

    degree: Mapped[list["Degree"]] = relationship(back_populates = "network")
    link: Mapped[list["Link"]] = relationship(back_populates = "network")
    pini: Mapped[list["Pini"]] = relationship(back_populates = "network")
    pfin: Mapped[list["Pfin"]] = relationship(back_populates = "network")
    
    
class Degree(Base):
    __tablename__ = "degree"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    position: Mapped[int]
    value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates = "degree")
    

class Link(Base):
    __tablename__ = "link"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    position: Mapped[int]
    value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates = "link")
    
    
class Pini(Base):
    __tablename__ = "pini"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    position: Mapped[int]
    value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates = "pini")
    
    
class Pfin(Base):
    __tablename__ = "pfin"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    position: Mapped[int]
    value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates = "pfin")
             


