from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Network(Base):
    __tablename__ = "network"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    label: Mapped[str]
    file_path: Mapped[str] 
    nodes: Mapped[Optional[int]] 
    edges: Mapped[Optional[int]] 
    is_read: Mapped[bool] = mapped_column(default=False)

    degree: Mapped[List["Degree"]] = relationship(back_populates="network")
    link: Mapped[List["Link"]] = relationship(back_populates="network")
    pini: Mapped[List["Pini"]] = relationship(back_populates="network")
    pfin: Mapped[List["Pfin"]] = relationship(back_populates="network")
    
    # def __repr__(self):
    #     return f"{self.__class__.__name__}(id={self.id}, label={self.label}, nodes={self.nodes}, edges={self.edges})"
    
    
class Degree(Base):
    __tablename__ = "degree"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    item_position: Mapped[int]
    item_value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates="degree")
    

class Link(Base):
    __tablename__ = "link"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    item_position: Mapped[int]
    item_value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates="link")
    
    
class Pini(Base):
    __tablename__ = "pini"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    item_position: Mapped[int]
    item_value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates="pini")
    
    
class Pfin(Base):
    __tablename__ = "pfin"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    item_position: Mapped[int]
    item_value: Mapped[int]
    
    network: Mapped["Network"] = relationship(back_populates="pfin")
             


