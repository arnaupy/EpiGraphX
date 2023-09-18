from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from . import models, schemas, tools


def pull_network(db: Session, network_id: str, features: list[str] | None = None) -> schemas.NetworkView | dict:
    
    db_network = db.query(models.Network).filter(models.Network.id == network_id).first()
    if not db_network:
        return None
    
    # Returns requested features
    if features:
        return {feature: jsonable_encoder(db_network)[feature] for feature in features}

    # Returns a 'NetworkView' object
    return tools.get_parent(db_network, schemas.NetworkView)



def pull_network_by_label(db: Session, label: str, features: list[str] | None = None) -> schemas.NetworkView | dict:
    
    db_network = db.query(models.Network).filter(models.Network.label == label).first()
    if not db_network:
        return None
    
    # Returns requested features
    if features:
        return {feature: jsonable_encoder(db_network)[feature] for feature in features}

    # Returns a 'NetworkView' object
    return tools.get_parent(db_network, schemas.NetworkView)
    

def pull_networks(db: Session, skip: int = 0, limit: int = 100, features: list | None = None
                  ) -> list[schemas.NetworkView] |list[dict]:  
    
    db_networks = db.query(models.Network).offset(skip).limit(limit).all()
    
    # Returns requested features
    if features:
        return [{feature: jsonable_encoder(network)[feature] for feature in features} for network in db_networks]

    # Returns a 'NetworkView' object
    return [tools.get_parent(network, schemas.NetworkView) for network in db_networks]