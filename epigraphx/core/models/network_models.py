"""
Database tables to python class interpreter:

    NAME -> models.py

    DESCRIPTION -> The main task of this file is to define database tables as python classes. To do so, it is used the
                   SQLAlchemy ORM module to build theses classes.

    CLASSES TODO
    |       
    +
"""
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

from ...config import system
from ..utils import database_utils

Base = declarative_base()

class DatabaseArrayMissmatchError(Exception):
    """Raises when any array coming from a database missmatch any specified attribute"""


class Network(Base):
    """Network table"""
    __tablename__ = "network"
    
    id: Mapped[str] = mapped_column(primary_key = True)
    label: Mapped[str]
    origin: Mapped[str] 
    is_private: Mapped[bool]
    is_scanned: Mapped[bool] = mapped_column(default = False)
    nodes: Mapped[Optional[int]] 
    edges: Mapped[Optional[int]] 
    last_update: Mapped[str]
    last_scan: Mapped[Optional[str]]
    time_to_scan: Mapped[Optional[str]]
    degree: Mapped["Degree"] = relationship(back_populates = "network")
    link: Mapped["Link"] = relationship(back_populates = "network")
    pini: Mapped["Pini"] = relationship(back_populates = "network")
    pfin: Mapped["Pfin"] = relationship(back_populates = "network")
    
    @hybrid_property
    def get_last_update(self) -> datetime:
        """Converts database last_update `str` into a `datetime` object"""
        
        return datetime.strptime(self.last_update, system.DATETIME_FORMAT)

    @hybrid_property
    def get_last_scan(self) -> datetime:
        """Converts database last_update `str` into a `datetime` object"""
        
        return datetime.strptime(self.last_scan, system.DATETIME_FORMAT)
    
    def update_last_changes(self):
        """Updates the `last_update` with the actual time"""
        
        self.last_update = database_utils.now()
        
    def update_last_scan(self):
        """Updates the `last_scan` with the actual time"""
        
        self.last_scan = database_utils.now()
    

class OneDimensionalDatabaseArray:
    """Base for one dimensional arrays stored in a SQL database"""
    
    id: Mapped[str] = mapped_column(primary_key = True)
    array: Mapped[str]
    dtype: Mapped[str]
    size: Mapped[int]
    
    @hybrid_property
    def value(self) -> np.ndarray:
        """Converts database array into a numpy array"""
        
        array = np.array(eval(self.array))
        assert array.dtype == self.dtype, DatabaseArrayMissmatchError(
            f"Database array type ({array.dtype}) missmatch specified type ({self.dtype}).")


        assert array.size == eval(self.size), DatabaseArrayMissmatchError(
            f"Database array size ({array.size}) type missmatch specified size ({eval(self.size)}).")
        
        return array
    
    
class Degree(Base, OneDimensionalDatabaseArray):
    """Network degree array table"""
    __tablename__ = "degree"
    
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    network: Mapped["Network"] = relationship(back_populates = "degree")
    
    
class Link(Base, OneDimensionalDatabaseArray):
    """Network link array table"""
    __tablename__ = "link"
    
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    network: Mapped["Network"] = relationship(back_populates = "link")
    
    
class Pini(Base, OneDimensionalDatabaseArray):
    """Network pini array table"""
    __tablename__ = "pini"
    
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    network: Mapped["Network"] = relationship(back_populates = "pini")
    
    
class Pfin(Base, OneDimensionalDatabaseArray):
    """Network pfin array table"""
    __tablename__ = "pfin"
    
    network_id: Mapped[str] = mapped_column(ForeignKey("network.id"))
    network: Mapped["Network"] = relationship(back_populates = "pfin")