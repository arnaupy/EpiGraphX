from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import numpy as np

from . import models, schemas 
from .tools import random_id
from .f2py.ReadNetwork import read_network as fortran_read_network


def create_network(db: Session, network: schemas.NetworkCreate) -> models.Network:
    db_network = models.Network(id = random_id(), label = network.label, file_path = network.file_path)
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return db_network



def pull_network(db: Session, network_id: str) -> models.Network:
    return db.query(models.Network).filter(models.Network.id == network_id).first()
    
    
    
def read_network(db: Session, network: schemas.Network) -> bool:
    # Reading process
    with open(network.file_path) as f:
        Emax = len(f.readlines())
    nodes, edges, link_array, degree_array, pini_array, pfin_array  = fortran_read_network(network.file_path, Emax)
    # output: (nodes, edges, link, degree, Pini, Pfin)
    link_array = np.trim_zeros(link_array)
    degree_array = np.trim_zeros(degree_array)
    pini_array = np.trim_zeros(pini_array)
    pfin_array = np.trim_zeros(pfin_array)

    # Updating networks table
    db.query(models.Network).filter(models.Network.id == network.id).update(
        {
            "nodes": nodes,
            "edges": edges,
            "is_read": True
            }
        )
                
    # Updating degree table
    degree_dict = [
        {
            "id": random_id(),
            "network_id": network.id,
            "position": node + 1,
            "value": int(degree)
            }
        for node, degree in enumerate(degree_array)
        ]
    db.bulk_insert_mappings(models.Degree, degree_dict)
                
    # Updating links table
    link_dict = [
        {
            "id": random_id(),
            "network_id": network.id,
            "position": edge + 1,
            "value": int(link)
            }
        for edge, link in enumerate(link_array)
        ]
    db.bulk_insert_mappings(models.Link, link_dict)
                
    # Updating pini table
    pini_dict = [
        {
            "id": random_id(),
            "network_id": network.id,
            "position": node + 1,
            "value": int(pini)
            }
        for node, pini in enumerate(pini_array)
        ]
    db.bulk_insert_mappings(models.Pini, pini_dict)
                
    # Updating pfin table
    pfin_dict = [
        {
            "id": random_id(),
            "network_id": network.id,
            "position": node + 1,
            "value": int(pfin)
            }
        for node, pfin in enumerate(pfin_array)
        ]
    db.bulk_insert_mappings(models.Pfin, pfin_dict)
                
    db.commit()
    return True



def update_network(db: Session, network: schemas.Network, network_update: schemas.NetworkUpdate) -> bool:
    
    update_item_encoded = jsonable_encoder(network_update)
    json_network = jsonable_encoder(network)
    
    for attribute in update_item_encoded:
        updated_attribute = update_item_encoded[attribute]
        if (updated_attribute != json_network[attribute]) and (updated_attribute != "None"):
            network.__setattr__(attribute, updated_attribute)
    db.add(network)
    db.commit()
    return True



def delete_network(db: Session, network: schemas.Network) -> bool:
    
    # In order to remove a network, every related object must be deleted
    db.query(models.Degree).filter(models.Degree.network_id == network.id).delete()
    db.query(models.Link).filter(models.Link.network_id == network.id).delete()
    db.query(models.Pini).filter(models.Pini.network_id == network.id).delete()
    db.query(models.Pfin).filter(models.Pfin.network_id == network.id).delete()
    db.query(models.Network).filter(models.Network.id == network.id).delete()
    db.commit()
    return True