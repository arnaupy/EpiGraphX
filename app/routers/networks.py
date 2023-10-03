"""
Main file where all the FastAPI requests are build:
|
|   NAME -> main.py
|
|   DESCRIPTION ->
|       
|    
"""
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from ..model import crud, schemas, models, summary, file_processors
from ..databases.postgresql import engine, get_db


models.Base.metadata.create_all(bind = engine)

router = APIRouter(prefix = "/networks", tags = ["networks"])


@router.post("/", response_model = schemas.Network)
def create_network(network: schemas.NetworkCreate, db: Session = Depends(get_db)):
    
    
    # Checks if 'Network label' is not already in use
    db_network = crud.pull_network_by_label(db = db, network_label = network.label)
    if db_network:
        raise HTTPException(status_code = 400, detail = "Network label is already in use")
    return crud.create_network(db = db, network = network)


@router.get("/")
def get_networks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                 features: list[str] = Query(default = None)):
    
    # Checks if features requested are attributes of 'Network' class
    if features:
        for feature in features:
            if feature not in models.Network.__dict__:
                raise HTTPException(
                    status_code = 400,
                    detail = f"Feature '{feature}' not in '{models.Network.__name__}' attributes"
                    )
    
    # Get a list of networks from the database
    db_networks = crud.pull_networks(db, skip = skip, limit = limit)
    
    return summary.describe_network(*db_networks, features = features)


@router.get("/{network_id}")
def get_network(network_id: str, db: Session = Depends(get_db), features: list[str] = Query(default = None)):
    
    # Checks if features requested are attributes of 'Network' class
    if features:
        for feature in features:
            if feature not in models.Network.__dict__:
                raise HTTPException(
                    status_code = 400,
                    detail = f"Feature '{feature}' not in '{models.Network.__name__}' attributes"
                    )

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if not db_network:
        raise HTTPException(status_code = 404, detail = "Network not found")
    
    return summary.describe_network(db_network, features = features)


@router.patch("/{network_id}")
def scan_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    
    # Checks if 'Network' is already read
    elif db_network.is_scanned == True:
        raise HTTPException(status_code = 400, detail = "Network is already scanned")
    
    # Checks that the network file is abailable to read
    processor = file_processors.get_file_processor(extension = ".txt", uploaded = True)

    # Checks that the file is already uploaded
    network_file = processor.pull(directory = "networks", filename = db_network.origin)
    if not network_file:
        raise HTTPException(status_code = 400, detail = f"Network file not found")

    return {"scanned" : crud.scan_network(db, network = db_network, network_file = network_file)}


@router.put("/{network_id}")
def update_network(network_id: str, network_update: schemas.NetworkUpdate, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    
    return {"updates": crud.update_network(db = db, network = db_network, network_update = network_update)}


@router.delete("/{network_id}")
def delete_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    return {"deleted": crud.delete_network(db, network = db_network)}



@router.get("/{network_id}/data", response_model = schemas.Network)
def get_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    return db_network




