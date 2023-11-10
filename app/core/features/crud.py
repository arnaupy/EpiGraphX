"""
CRUD functionalities:

    NAME -> crud.py

    DESCRIPTION -> This file implement `create` & `read` & `update` & `delete` basic API functionalities.
    
    PUBLIC FUNCTIONS
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
    |
    |
    |   * describe_network -> TODO
    |
    +
    
    PRIVATE FUNCTIONS
    |
    |   * _get_parent -> TODO
    +
"""
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import time
import numpy as np
import validators

from ..schemas import network_schemas
from ..models import network_models, file_models
from ..processors import file_processor
from ..utils import database_utils
from ..f2py.ReadNetwork import read_network as f2p2_scan_network
    

def create_network(db: Session, network: network_schemas.NetworkCreate) -> network_models.Network:
    """Takes a network create object and registers the network in the database returning this network"""  

    db_network = network_models.Network(id = database_utils.random_id(),
                                        label = network.label,
                                        origin = network.origin,
                                        is_private = network.is_private,
                                        last_update = database_utils.now())
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return db_network


def pull_networks(db: Session, skip: int = 0, limit: int = 100) -> list[network_models.Network]:
    """Call network list from the database"""
    return db.query(network_models.Network).offset(skip).limit(limit).all()


def pull_network_by_label(db: Session, network_label: str) -> network_models.Network:
    """Call the network object from the database by its label"""
    return db.query(network_models.Network).filter(network_models.Network.label == network_label).first()


def pull_network(db: Session, network_id: str) -> network_models.Network:
    """Call the network object from the database by its id"""
    return db.query(network_models.Network).filter(network_models.Network.id == network_id).first()
    
    
def scan_network(db: Session, network: network_models.Network, network_file = file_models.NetworkFile) -> bool:
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
    network.degree = network_models.Degree(id = database_utils.random_id(), network_id = network.id, 
                                   array = str(degree_array.tolist()), dtype = str(degree_array.dtype),
                                   size = degree_array.size) 
    
    link_array = np.trim_zeros(link_array)
    network.link = network_models.Link(id = database_utils.random_id(), network_id = network.id, 
                                   array = str(link_array.tolist()), dtype = str(link_array.dtype),
                                   size = link_array.size) 
    
    pini_array = np.trim_zeros(pini_array)
    network.pini = network_models.Pini(id = database_utils.random_id(), network_id = network.id, 
                                   array = str(pini_array.tolist()), dtype = str(pini_array.dtype),
                                   size = pini_array.size) 
    
    pfin_array = np.trim_zeros(pfin_array)
    network.pfin = network_models.Pfin(id = database_utils.random_id(), network_id = network.id, 
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


def update_network(db: Session, network: network_models.Network, network_update: network_schemas.NetworkUpdate) -> dict[str, str]:
    """Updates the network attributes that are allowed to be updated"""
    
    updates = {}
    # Dictionary with attributes as keys and updates as values
    # Only `NetworkUpdate` attrbutes that are assigned are dumped into the dictionary
    attributes_to_update = network_update.model_dump(exclude_unset = True)
    
    # Updates network object
    for attribute, updated_attribute in attributes_to_update.items():
        
        # Check if the update is different that the actual value
        if updated_attribute != getattr(network, attribute): 
            updates.update({attribute: f"{getattr(network, attribute)} -> {updated_attribute}"})
            setattr(network, attribute, updated_attribute)

    network.update_last_changes()  
    db.add(network)
    db.commit()
    return updates


def delete_network(db: Session, network: network_models.Network) -> bool:
    """Delete the network from the database including its relationships"""
    
    # In order to remove a network, every related object must be deleted
    db.query(network_models.Degree).filter(network_models.Degree.network_id == network.id).delete()
    db.query(network_models.Link).filter(network_models.Link.network_id == network.id).delete()
    db.query(network_models.Pini).filter(network_models.Pini.network_id == network.id).delete()
    db.query(network_models.Pfin).filter(network_models.Pfin.network_id == network.id).delete()
    db.query(network_models.Network).filter(network_models.Network.id == network.id).delete()
    db.commit()
    return True


def _get_parent(child, parent_class):
    """
    Method to build a 'parent-pydantic-BaseModel' class from its child. 
    That way getting rid of extra child attributes.
    """
    
    parent_attributes = {}
    # Looks for shared attributes shared among parent and child
    for attribute in jsonable_encoder(child):
        if attribute in parent_class.model_json_schema()["properties"]:
            parent_attributes.update({attribute: jsonable_encoder(child)[attribute]})
    return parent_class(**parent_attributes)


def describe_network(*db_networks: list[network_models.Network] | network_models.Network, features: list[str] | None = None
             ) -> list[network_schemas.NetworkSummary] | network_schemas.NetworkSummary | dict:
    """Pull the `schemas.NetworkSummary` object out of `schemas.Network`"""
    
    # Returns requested features
    if features:
        return [{feature: jsonable_encoder(network)[feature] for feature in features} for network in db_networks]

    # Returns a 'NetworkSummary' object
    described_networks = [_get_parent(network, network_schemas.NetworkSummary) for network in db_networks]
    
    # If there is only one network, it doesn't return the list object 
    if len(described_networks) == 1:
        return described_networks[0]
    return described_networks
