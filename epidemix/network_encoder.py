from typing import Optional
# from typing import List

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
    
    id: Mapped[str] = mapped_column(primary_key=True)
    label: Mapped[str] 
    nodes: Mapped[Optional[int]] 
    edges: Mapped[Optional[int]] 
    is_read: Mapped[bool]
    file_path: Mapped[str]
    # degrees: Mapped[List["Degree"]] = relationship(back_populates="network")
    # links: Mapped[List["Link"]] = relationship(back_populates="network")
    # pini: Mapped[List["Pini"]] = relationship(back_populates="network")
    # pfin: Mapped[List["Pfin"]] = relationship(back_populates="network")
    
    def __init__(self, label, file_path = None):
        # Creates a new session
        with Session(expire_on_commit = False) as session:
            # Registration on a new network
            if not(exists(label)):
                assert file_path != None, f"(400 BAD REQUEST):'{label}' do not exist, a file path is needed"
                self.id = random_id()
                self.label = label
                self.file_path = file_path
                self.is_read = False
                session.add(self)
                session.commit()
                print(f"(201 CREATED): Network '{self.id}' registered in the system")
            # Instanciation of an existing network
            else:
                if file_path != None:
                    print("WARNING: File path is not needed when calling read_network function in a registered network")
                # Get existing data
                network = session.query(Network).filter(Network.label == label).first()
                columns = network.__table__.columns
                for column in columns:
                    column_name = column.name
                    setattr(self, column_name, network.__getattribute__(column_name))
                print(f"(200 OK): Network '{self.id}' instanciated")
        
        
    def __repr__(self):
        if self.is_read:
            return f"{self.__class__.__name__}(label = {self.label}, nodes = {self.nodes}, edges = {self.edges})" 
    
        else:
            return f"{self.__class__.__name__}(label = {self.label})"
    
    
    
    def read_network(self,return_tables = False):
           
        # Checks if network is already read
        assert not(self.is_read), f"(400 BAD REQUEST): Network named '{self.label}' saved in file '{self.file_path}' is already read."
        
        
        # Reading process
        with open(self.file_path) as f:
            Emax = len(f.readlines())
        self.nodes, self.edges, self.links, self.degree, self.pini, self.pfin = read_network(self.file_path, Emax)
        # network_data = (N, E, links, degree, Pini, Pfin)
        self.is_read = True
        
        session = Session()

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
                    "item_value": int(self.degree[node])
                 }
                for node in range(self.nodes)
            ]
        session.bulk_insert_mappings(Degree, degree_dict)
        
        # Updating links table
        links_dict = [
                {
                    "id": random_id(),
                    "network_id": self.id,
                    "item_position": edge + 1,
                    "item_value": int(self.links[edge])
                 }
                for edge in range(self.edges)
            ]
        session.bulk_insert_mappings(Link, links_dict)
        
        # Updating pini table
        pini_dict = [
                {
                    "id": random_id(),
                    "network_id": self.id,
                    "item_position": node + 1,
                    "item_value": int(self.pini[node])
                 }
                for node in range(self.nodes)
            ]
        session.bulk_insert_mappings(Pini, pini_dict)
        
        # Updating pfin table
        pfin_dict = [
                {
                    "id": random_id(),
                    "network_id": self.id,
                    "item_position": node + 1,
                    "item_value": int(self.pfin[node])
                 }
                for node in range(self.nodes)
            ]
        session.bulk_insert_mappings(Pfin, pfin_dict)
        
        
        # Commit updates
        session.commit()
        # Session is closed
        session.close()
        print(f"(201 CREATED): Network ({self.id}) read")
        if return_tables:
            return degree_dict, links_dict, pini_dict, pfin_dict
        
    def update(self, **kwargs):
        non_updatable_attributes = ["nodes", "edges", "is_read"]
        for attribute_name, attribute_value in kwargs.items():
            if attribute_name in non_updatable_attributes:
                print(f"(WARNING): attribute '{attribute_name}' can not be updated")
            else:
                setattr(self, attribute_name, attribute_value)
    
        # Creates a new session
        with Session(expire_on_commit = False) as session:
            session.execute(
                update(self.__class__)
                .where(self.__class__.id == self.id)
                .values(**kwargs)
                )
            session.commit()
        
Object = create_vector_table(int, class_name="Degree")
class Degree(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"))
    # network: Mapped[Network] = relationship(back_populates="degrees")

Object = create_vector_table(int, class_name="Link")
class Link(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"))
    # network: Mapped[Network] = relationship(back_populates="links")

Object = create_vector_table(int, class_name="Pini")
class Pini(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"))
    # network: Mapped[Network] = relationship(back_populates="pini")
    

Object = create_vector_table(int, class_name="Pfin")
class Pfin(Object):
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"))
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
        
    
    
def list_networks() -> list:
    """(list_networks)

    Returns:
        list: contains every network registered in the system
    """
    with Session() as session:
        result = session.query(Network).all()
    print(f"(200 OK): Showing networks registered in the system!")
    return result

    
    
# def get_array(self, array_table):
#     # Creates a new session
#     session = Session()
        
#     result = session.query(array_table).filter(array_table.network_id == self.id)
#     # Session is closed
#     session.close()
#     return result
    

    