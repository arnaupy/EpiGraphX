"""
CRUD functionalities:

    NAME -> crud.py

    DESCRIPTION -> This file implement `create` & `read` & `update` & `delete` basic API functionalities.
    
    FUNCTIONS:
    |
    |   * create_network -> creates a network in the database
    |       
    |       inputs: 
    |           - db(Session): database connection
    |           - network(schemas.NetworkCreate): network pydantic schema to create a network
    |            
    |       output: (models.Network) -> The database network object created
    |
    |
    |   * pull_network -> returns the a network by its id
    |       
    |       inputs: 
    |           - db(Session): database connection
    |           - network_id(str): database network id
    |            
    |       output: (models.Network) -> The database network object pulled
    |
    |
    |   * scan_network -> scan a network updating its data in the database
    |       
    |       inputs: 
    |           - db(Session): database connection
    |           - network(models.Network): database network to read
    |           - network_file(file_processors.NetworkFile): network file instance
    |            
    |       output: (bool) -> Returns `True` if no error was raised and network was scanned and updated correctly
    |
    |
    |   * upload_network -> upload network `label` or `origin` (and `is_private` as a consequence of `origin`)
    |       
    |       inputs: 
    |           - db(Session): database connection
    |           - network(models.Network): database network to upload
    |           - network_update(schemas.NetworkUpdate): network update schema
    |            
    |       output: (dict[str, str]) -> Changes dict where keys can be `label` or/and `origin` and values the updates
    |
    |
    |   * delete_network -> delete a network form the database
    |       
    |       inputs: 
    |           - db(Session): database connection
    |           - network(models.Network): database network to delete
    |            
    |       output: (bool) -> Returns `True` if no error was raised and network was deleted correctly
    +
"""
from sqlalchemy.orm import Session
import time
import numpy as np

from . import schemas, models, file_processors
from .. import tools
from .f2py.ReadNetwork import read_network as f2p2_scan_network
    

def create_network(db: Session, network: schemas.NetworkCreate) -> models.Network:
    """Takes a network create object and registers the network in the database returning this network"""  
    
    # network_file_processor = get_file_processor(network.is_private)

    db_network = models.Network(id = tools.random_id(),
                                label = network.label,
                                origin = network.origin,
                                is_private = network.is_private,
                                last_update = tools.now(dateformat = models.DATETIME_FORMAT))
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return db_network

def pull_networks(db: Session, skip: int = 0, limit: int = 100) -> list[models.Network]:
    """Call network list from the database"""
    return db.query(models.Network).offset(skip).limit(limit).all()

def pull_network_by_label(db: Session, network_label: str) -> models.Network:
    """Call the network object from the database by its label"""
    return db.query(models.Network).filter(models.Network.label == network_label).first()

def pull_network(db: Session, network_id: str) -> models.Network:
    """Call the network object from the database by its id"""
    return db.query(models.Network).filter(models.Network.id == network_id).first()
    
    
def scan_network(db: Session, network: models.Network, network_file = file_processors.NetworkFile) -> bool:
    """Scan the network from a 'txt' file"""
    
    # Since Fortran does not dynamically expand vector size, a maximum vector size must be selected.
    # The maximum size can be set to the number of rows in the file, as this represents the maximum number of edges.
    # If each row in the file corresponds to a single edge and there is no duplication, then this number can serve as the maximum.
    timer_ini = time.time()
    with open(network_file.path) as f:
        Emax = len(f.readlines())
    nodes, edges, link_array, degree_array, pini_array, pfin_array  = f2p2_scan_network(network_file.path, Emax)
    # output: (nodes, edges, link, degree, Pini, Pfin)
    timer_fin = time.time()
    
    # Stores the time it took to scan the network
    network.time_to_scan = round(timer_fin - timer_ini, 3)
    
    # Stores the four network vectors
    degree_array = np.trim_zeros(degree_array)
    network.degree = models.Degree(id = tools.random_id(), network_id = network.id, 
                                   array = str(degree_array.tolist()), dtype = str(degree_array.dtype),
                                   size = degree_array.size) 
    
    link_array = np.trim_zeros(link_array)
    network.link = models.Link(id = tools.random_id(), network_id = network.id, 
                                   array = str(link_array.tolist()), dtype = str(link_array.dtype),
                                   size = link_array.size) 
    
    pini_array = np.trim_zeros(pini_array)
    network.pini = models.Pini(id = tools.random_id(), network_id = network.id, 
                                   array = str(pini_array.tolist()), dtype = str(pini_array.dtype),
                                   size = pini_array.size) 
    
    pfin_array = np.trim_zeros(pfin_array)
    network.pfin = models.Pfin(id = tools.random_id(), network_id = network.id, 
                                   array = str(pfin_array.tolist()), dtype = str(pfin_array.dtype),
                                   size = pfin_array.size)  
    
    # Updates other network attributes
    network.nodes, network.edges, network.is_scanned = nodes, edges, True

    # Updates the timers and commit changes
    network.update_last_scan()    
    network.update_last_changes()    
    db.add(network)        
    db.commit()
    return True


def update_network(db: Session, network: models.Network, network_update: schemas.NetworkUpdate) -> dict[str, str]:
    """Updates the network attributes that are allowed to be updated"""
    
    updates = {}
    attributes_to_update = network_update.model_dump(exclude_unset = True)
    for attribute, updated_attribute in attributes_to_update.items():
        if updated_attribute != getattr(network, attribute): 
            updates.update({attribute: f"{getattr(network, attribute)} -> {updated_attribute}"})
            setattr(network, attribute, updated_attribute)

    network.update_last_changes()  
    db.add(network)
    db.commit()
    return updates


def delete_network(db: Session, network: models.Network) -> bool:
    """Delete the network from the database including its relationships"""
    
    # In order to remove a network, every related object must be deleted
    db.query(models.Degree).filter(models.Degree.network_id == network.id).delete()
    db.query(models.Link).filter(models.Link.network_id == network.id).delete()
    db.query(models.Pini).filter(models.Pini.network_id == network.id).delete()
    db.query(models.Pfin).filter(models.Pfin.network_id == network.id).delete()
    db.query(models.Network).filter(models.Network.id == network.id).delete()
    db.commit()
    return True


