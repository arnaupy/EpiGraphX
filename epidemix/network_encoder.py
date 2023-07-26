from typing import Optional
# from typing import List

import numpy as np

from sqlalchemy import ForeignKey
from sqlalchemy import update
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship

from utils.ReadNetwork import read_network 
from utils.base import Session
from utils.base import engine
from utils.base import Base
from utils.tools import random_id
from utils.vector import create_vector_table
      
      
class Network(Base):
    __tablename__ = "networks"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[str] = mapped_column(primary_key=True)
    label: Mapped[str] 
    nodes: Mapped[Optional[int]] 
    edges: Mapped[Optional[int]] 
    is_read: Mapped[bool]
    file_path: Mapped[Optional[str]]
    # degrees: Mapped[List["Degree"]] = relationship(back_populates="network")
    # links: Mapped[List["Link"]] = relationship(back_populates="network")
    # pini: Mapped[List["Pini"]] = relationship(back_populates="network")
    # pfin: Mapped[List["Pfin"]] = relationship(back_populates="network")
        
             
    def __repr__(self):
        class_name = self.__class__.__name__
        if exists(self.label):
            if self.is_read:
                return f"{class_name}(label = {self.label}, nodes = {self.nodes}, edges = {self.edges})" 
        
            else:
                return f"{class_name}(label = {self.label})"
        else:
            return f"{class_name}(file_path = {self.file_path})"
    
    @classmethod
    def from_file_path(cls, file_path):
        class_object = cls(file_path=file_path)
        class_object.is_read = False
        return class_object
    
    @classmethod
    def from_db(cls, label):
        with Session() as session:
            if exists(label):
                network = session.query(Network).filter(Network.label == label).first()
            else:
                print(f"(404 NOT-FOUND): Network '{label}' is not registered in the system")
                return "ERROR: 404"
        print(f"(201 CREATED): Network successfully instanciated")
        return network
    
    
    def register(self, label):
        if exists(label):
            print(f"(400 BAD-REQUEST): Network '{label}' is already registered in the system")
            return "ERROR_ 400"
            
        # Creates a new session
        with Session(expire_on_commit = False) as session: 
            self.id = random_id()
            self.label = label
            session.bulk_insert_mappings(Network, [
                {
                    "id": self.id,
                    "label": self.label,
                    "is_read": self.is_read,
                    "file_path": self.file_path
                    }
                ]
                                         )
            session.commit()
            
        print(f"(201 CREATED): Network successfully registered in the system")
        if self.is_read:
            self.upload()

    
    def read_network(self, return_tables = False, upload = False):
           
        # Checks if network is already read
        assert not(self.is_read), f"(ERROR): Network is already read"
        
        
        # Reading process
        print("(NOTE): Reading network...")
        with open(self.file_path) as f:
            Emax = len(f.readlines())
        self.nodes, self.edges, self.links, self.degrees, self.pini, self.pfin = read_network(self.file_path, Emax)
        # network_data = (N, E, links, degree, Pini, Pfin)
        self.links, self.degrees, self.pini, self.pfin = (
            np.trim_zeros(self.links),
            np.trim_zeros(self.degrees),
            np.trim_zeros(self.pini),
            np.trim_zeros(self.pfin)
            )
        
        print("(NOTE): Network successfuly read")
        self.is_read = True
        
        if upload:
            self.upload()
            
        
    def upload(self):
        print("(NOTE): Uploading network...")
        assert exists(self.label), f"""(400 BAD-REQUEST): Can not upload a non register network. 
        (ADVISE): Try to register it. The network will be automatically uploaded once it is registered."""
        
        with Session(expire_on_commit = False) as session:
            # Updating networks table
            session.query(Network).filter(Network.id == self.id).update(
                {
                    "nodes": self.nodes,
                    "edges": self.edges,
                    "is_read": self.is_read
                }
                )
                
            # Updating degree table
            degree_dict = [
                    {
                        "id": random_id(),
                        "network_id": self.id,
                        "item_position": node + 1,
                        "item_value": int(degree)
                    }
                    for node, degree in enumerate(self.degrees)
                ]
            session.bulk_insert_mappings(Degree, degree_dict)
                
            # Updating links table
            links_dict = [
                    {
                        "id": random_id(),
                        "network_id": self.id,
                        "item_position": edge + 1,
                        "item_value": int(link)
                    }
                    for edge, link in enumerate(self.links)
                ]
            session.bulk_insert_mappings(Link, links_dict)
                
            # Updating pini table
            pini_dict = [
                    {
                        "id": random_id(),
                        "network_id": self.id,
                        "item_position": node + 1,
                        "item_value": int(pini)
                    }
                    for node, pini in enumerate(self.pini)
                ]
            session.bulk_insert_mappings(Pini, pini_dict)
                
            # Updating pfin table
            pfin_dict = [
                    {
                        "id": random_id(),
                        "network_id": self.id,
                        "item_position": node + 1,
                        "item_value": int(pfin)
                    }
                    for node, pfin in enumerate(self.pfin)
                ]
            session.bulk_insert_mappings(Pfin, pfin_dict)
                
            # Commit changes
            session.commit()
            
        print(f"(201 CREATED): Network uploaded")

        
    def update(self, **kwargs):
        non_updatable_attributes = ["nodes", "edges", "is_read"]
        changes = dict()
        for attribute_name, attribute_value in kwargs.items():
            if attribute_name in non_updatable_attributes:
                print(f"(WARNING): attribute '{attribute_name}' can not be updated")
            else:
                changes.update({attribute_name : attribute_value})
                setattr(self, attribute_name, attribute_value)

        if len(changes) != 0:
            # Creates a new session
            with Session(expire_on_commit = False) as session:
                session.execute(
                    update(self.__class__)
                    .where(self.__class__.id == self.id)
                    .values(changes)
                    )
                session.commit()
        else:
            print(f"(400 BAD REQUEST): No changes to update")
        
Object = create_vector_table(int, class_name="Degree")
class Degree(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"), use_existing_column=True)
    # network: Mapped[Network] = relationship(back_populates="degrees")

Object = create_vector_table(int, class_name="Link")
class Link(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"), use_existing_column=True)
    # network: Mapped[Network] = relationship(back_populates="links")

Object = create_vector_table(int, class_name="Pini")
class Pini(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"), use_existing_column=True)
    # network: Mapped[Network] = relationship(back_populates="pini")
    

Object = create_vector_table(int, class_name="Pfin")
class Pfin(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"), use_existing_column=True)
    # network: Mapped[Network] = relationship(back_populates="pfin")
    
Object.metadata.create_all(engine)


def exists(network_label:str) -> bool:
    """(exists)

    Args:
        network_label (str): label of the network

    Returns:
        bool: True if the label is associated with a network in the system. False otherwise
    """
    with Session() as session:
        result = session.query(Network).filter(Network.label == network_label).count() != 0
    return result
    
def remove_network(network_label:str):
    """(remove_network)

    Args:
        network_label (str): label of the network to remove from the system
    """

    try:
        with Session() as session:
            network_id = session.query(Network).filter(Network.label == network_label).first().id
            
            # Drops every vector table associated networks table
            network_referenced_tables = [Degree, Link, Pini, Pfin]
            for referenced_table in network_referenced_tables:
                (
                    session
                    .query(referenced_table)
                    .filter(referenced_table.network_id == network_id)
                    .delete()
                )
            # Drops the network entry associated with the label
            session.query(Network).filter(Network.id == network_id).delete()
            session.commit()
        print(f"(200 OK): Network '{network_id}' removed")
        
    except:
        print(f"(404 NOT FOUND): There is no network named '{network_label}' in the system")
        

    
    
# def get_array(self, array_table):
#     # Creates a new session
#     session = Session()
        
#     result = session.query(array_table).filter(array_table.network_id == self.id)
#     # Session is closed
#     session.close()
#     return result
    

    