from panpy.utils.ReadNetwork import read_network 
import warnings
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from utils.base import Session, engine, Base

# from sqlalchemy.orm import sessionmaker
      
      
class Network(Base):
    __tablename__ = "networks"
    
    id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    label = Column("label", String, nullable = False)
    nodes = Column("nodes", Integer)
    edges = Column("edges", Integer)
    is_read = Column("is_read", Boolean)
    file_path = Column("file_path", String, nullable = False)
    
    def __init__(self, label, file_path = None):
        # Creates a new session
        session = Session()
        network_exists = exists(label)
        if not(network_exists):
            assert file_path != None, f"({label}) do not exist, a file path is needed"
            self.label = label
            self.file_path = file_path
            self.is_read = False
            session.add(self)
            session.commit()
            
        else:
            if file_path != None:
                warnings.warn("File path is not needed when calling read_network function in a registered network.")
        # Get existing data
        network = session.query(Network).filter(Network.label == label).first()
        self.label = network.label
        self.id = network.id
        self.is_read = network.is_read
        self.file_path = network.file_path
        if self.is_read:
            self.nodes = network.nodes
            self.edges = network.edges
        
        # Session is closed
        session.close()
        
        
    def __repr__(self):
        if self.is_read:
            return f"({self.id}) {self.label} : N = {self.nodes} : E = {self.edges}" 
        else:
            return f"({self.id}) {self.label} not read yet"
    
    
    
    def read_network(self, update = False, return_tables = False):
           
        # Checks if network is already read
        if not(update): 
            assert not(self.is_read), f"Network named ({self.label}) saved in file ({self.file_path}) is already read."
        else:
            assert self.is_read, f"Can not update a non-read network."
            
        
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
        
        # Updating vector tables
        degree_dict = [
                {
                    "network_id": self.id,
                    "item_position": node + 1,
                    "item_value": int(self.degree[node])
                 }
                for node in range(self.nodes)
            ]
        
        links_dict = [
                {
                    "network_id": self.id,
                    "item_position": edge + 1,
                    "item_value": int(self.links[edge])
                 }
                for edge in range(self.edges)
            ]
        
        pini_dict = [
                {
                    "network_id": self.id,
                    "item_position": node + 1,
                    "item_value": int(self.pini[node])
                 }
                for node in range(self.nodes)
            ]
        
        pfin_dict = [
                {
                    "network_id": self.id,
                    "item_position": node + 1,
                    "item_value": int(self.pfin[node])
                 }
                for node in range(self.nodes)
            ]
        
        session.bulk_insert_mappings(Degree, degree_dict)
        session.bulk_insert_mappings(Link, links_dict)
        session.bulk_insert_mappings(Pini, pini_dict)
        session.bulk_insert_mappings(Pfin, pfin_dict)
        
        # Commit updates
        session.commit()
        # Session is closed
        session.close()
        print(f"Network ({self.id}) '{self.label}' successfuly read")
        if return_tables:
            return degree_dict, links_dict, pini_dict, pfin_dict
    
class Degree(Base):
    __tablename__ = "degree"
    
    id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    network_id = Column("network_id", Integer, ForeignKey("networks.id"), nullable = False)
    item_position = Column("item_position", Integer, nullable = False)
    item_value = Column("item_value", Integer, nullable = False)
    
    def __init__(self, network_id, item_position, item_value):
        self.network_id = network_id
        self.item_position = item_position
        self.item_value = item_value
        
        
    def __repr__(self):
        return f"({self.network_id}) {self.__tablename__} : pos({self.item_position}) : value({self.item_value})" 
    


class Link(Base):
    __tablename__ = "links"
    
    id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    network_id = Column("network_id", Integer, ForeignKey("networks.id"), nullable = False)
    item_position = Column("item_position", Integer, nullable = False)
    item_value = Column("item_value", Integer, nullable = False)
    
    def __init__(self, network_id, item_position, item_value):
        self.network_id = network_id
        self.item_position = item_position
        self.item_value = item_value
        
        
    def __repr__(self):
        return f"({self.network_id}) {self.__tablename__} : pos({self.item_position}) : value({self.item_value})" 
    

class Pini(Base):
    __tablename__ = "pini"
    
    id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    network_id = Column("network_id", Integer, ForeignKey("networks.id"), nullable = False)
    item_position = Column("item_position", Integer, nullable = False)
    item_value = Column("item_value", Integer, nullable = False)
    
    def __init__(self, network_id, item_position, item_value):
        self.network_id = network_id
        self.item_position = item_position
        self.item_value = item_value
        
        
    def __repr__(self):
        return f"({self.network_id}) {self.__tablename__} : pos({self.item_position}) : value({self.item_value})" 
    

class Pfin(Base):
    __tablename__ = "pfin"
    
    id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    network_id = Column("network_id", Integer, ForeignKey("networks.id"), nullable = False)
    item_position = Column("item_position", Integer, nullable = False)
    item_value = Column("item_value", Integer, nullable = False)
    
    def __init__(self, network_id, item_position, item_value):
        self.network_id = network_id
        self.item_position = item_position
        self.item_value = item_value
        
        
    def __repr__(self):
        return f"({self.network_id}) {self.__tablename__} : pos({self.item_position}) : value({self.item_value})" 

Base.metadata.create_all(engine)

def exists(network_label) -> bool:
        # Creates a new session
        session = Session()
        # Checks if the network label is on the networks table
        result = session.query(Network).filter(Network.label == network_label).count() != 0
        # Session is closed
        session.close()
        
        return result
    
def remove_network(network_label):
    session = Session()
    network_id = session.query(Network).filter(Network.label == network_label).first().id
    session.query(Degree).filter(Degree.network_id == network_id).delete()
    session.query(Link).filter(Link.network_id == network_id).delete()
    session.query(Pini).filter(Pini.network_id == network_id).delete()
    session.query(Pfin).filter(Pfin.network_id == network_id).delete()
    session.query(Network).filter(Network.id == network_id).delete()
    session.commit()
    session.close()
    
    print(f"({network_id})'{network_label}' successfuly removed from Networks table")
    
def list_networks():
    session = Session()
    result = session.query(Network).all()
    session.close()
    return result
    
    
def get_array(self, array_table):
    # Creates a new session
    session = Session()
        
    result = session.query(array_table).filter(array_table.network_id == self.id)
    # Session is closed
    session.close()
    return result
    

    