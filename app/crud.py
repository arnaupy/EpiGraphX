from sqlalchemy.orm import Session
from . import models, schemas 
from .utils.tools import random_id
from .f2py.ReadNetwork import read_network as fortran_read_network
import numpy as np


def pull_network(db: Session, network_id: str) -> models.Network:
    return db.query(models.Network).filter(models.Network.id == network_id).first()


def pull_network_by_label(db: Session, label: str) -> models.Network:
    return db.query(models.Network).filter(models.Network.label == label).first()


def pull_networks(db: Session, skip: int = 0, limit: int = 100, show_id: bool = False) -> list:
    if show_id:
        return [id[0] for id in db.query(models.Network.id).offset(skip).limit(limit).all()]
    return db.query(models.Network).offset(skip).limit(limit).all()


def register_network(db: Session, network: schemas.NetworkCreate) -> models.Network:
    db_network = models.Network(id = random_id(), label = network.label, file_path = network.file_path)
    db.add(db_network)
    db.commit()
    db.refresh(db_network)
    return db_network

def remove_network(db: Session, network: schemas.Network):
    db.query(models.Degree).filter(models.Degree.network_id == network.id).delete()
    db.query(models.Link).filter(models.Link.network_id == network.id).delete()
    db.query(models.Pini).filter(models.Pini.network_id == network.id).delete()
    db.query(models.Pfin).filter(models.Pfin.network_id == network.id).delete()
    db.query(models.Network).filter(models.Network.id == network.id).delete()
    db.commit()
    return True
    
    
def read_network(db: Session, network: schemas.Network):
    # Reading process
    with open(network.file_path) as f:
        Emax = len(f.readlines())
    nodes, edges, link_array, degree_array, pini_array, pfin_array  = fortran_read_network(network.file_path, Emax)
    # network_data = (N, E, links, degree, Pini, Pfin)
    link_array, degree_array, pini_array, pfin_array = (
        np.trim_zeros(link_array), 
        np.trim_zeros(degree_array),
        np.trim_zeros(pini_array),
        np.trim_zeros(pfin_array))
    
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
                "item_position": node + 1,
                "item_value": int(degree)
            }
            for node, degree in enumerate(degree_array)
        ]
    db.bulk_insert_mappings(models.Degree, degree_dict)
                
    # Updating links table
    link_dict = [
            {
                "id": random_id(),
                "network_id": network.id,
                "item_position": edge + 1,
                "item_value": int(link)
            }
            for edge, link in enumerate(link_array)
        ]
    db.bulk_insert_mappings(models.Link, link_dict)
                
    # Updating pini table
    pini_dict = [
            {
                "id": random_id(),
                "network_id": network.id,
                "item_position": node + 1,
                "item_value": int(pini)
            }
            for node, pini in enumerate(pini_array)
        ]
    db.bulk_insert_mappings(models.Pini, pini_dict)
                
    # Updating pfin table
    pfin_dict = [
            {
                "id": random_id(),
                "network_id": network.id,
                "item_position": node + 1,
                "item_value": int(pfin)
            }
            for node, pfin in enumerate(pfin_array)
        ]
    db.bulk_insert_mappings(models.Pfin, pfin_dict)
                
    # Commit changes
    db.commit()
    return pull_network(db = db, network_id = network.id)


def pull_degree(db: Session, degree_id: str) -> models.Network:
    return db.query(models.Degree).filter(models.Degree.id == degree_id).first()


def pull_degree_by_attributes(db: Session, network_id: str, item_position: int, item_value: int):
    return db.query(models.Degree).filter((models.Degree.network_id == network_id) & 
                                          (models.Degree.item_position == item_position) &
                                          (models.Degree.item_value == item_value)
                                          ).first()

def add_degree(db: Session, degree: schemas.DegreeCreate):
    db_degree = models.Degree(id = random_id(), 
                              network_id = degree.network_id, 
                              item_position = degree.item_position, 
                              item_value = degree.item_value
                              )
    db.add(db_degree)
    db.commit()
    db.refresh(db_degree)
    return db_degree
    
        
def remove_degree(db: Session, degree: schemas.Degree):
    db.query(models.Degree).filter(models.Degree.id == degree.id).delete()
    db.commit()
    return True
    

