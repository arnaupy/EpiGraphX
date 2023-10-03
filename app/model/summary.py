"""
File used to send only the non-relational attributes of the SQL database tables:

    NAME -> summary.py

    DESCRIPTION -> TODO
        
    CLASSES: TODO
    |       
    +
"""
from fastapi.encoders import jsonable_encoder

from . import schemas, models


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


def describe_network(*db_networks: list[models.Network] | models.Network, features: list[str] | None = None
             ) -> list[schemas.NetworkSummary] | schemas.NetworkSummary | dict:
    """Pull the `schemas.NetworkSummary` object out of `schemas.Network`"""
    
    # Returns requested features
    if features:
        return [{feature: jsonable_encoder(network)[feature] for feature in features} for network in db_networks]

    # Returns a 'NetworkSummary' object
    described_networks = [_get_parent(network, schemas.NetworkSummary) for network in db_networks]
    
    # If there is only one network, it doesn't return the list object 
    if len(described_networks) == 1:
        return described_networks[0]
    return described_networks
    