from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from . import crud, models, schemas, view
from .database import SessionLocal, engine
from app import __version__

models.Base.metadata.create_all(bind = engine)

app = FastAPI(
    version = __version__
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/networks/", response_model = schemas.Network)
def create_network(network: schemas.NetworkCreate, db: Session = Depends(get_db)):
    
    # Checks if 'Network label' is not already in use
    db_network = view.pull_network_by_label(db = db, label = network.label)
    if db_network:
        raise HTTPException(status_code = 400, detail = "Network label is already in use")
    return crud.create_network(db = db, network = network)



@app.get("/networks/")
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
                
    networks_view = view.pull_networks(db, skip = skip, limit = limit, features = features)
    return networks_view



@app.get("/networks/{network_id}")
def get_network(network_id: str, db: Session = Depends(get_db), features: list[str] = Query(default = None)):
    
    # Checks if features requested are attributes of 'Network' class
    if features:
        for feature in features:
            if feature not in models.Network.__dict__:
                raise HTTPException(
                    status_code = 400,
                    detail = f"Feature '{feature}' not in '{models.Network.__name__}' attributes"
                    )

    network_view = view.pull_network(db, network_id = network_id, features = features)
    
    # Checks if 'Network id' is registered in the database
    if network_view is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    return network_view



@app.patch("/networks/{network_id}")
def read_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    
    # Checks if 'Network' is already read
    elif db_network.is_read == True:
        raise HTTPException(status_code = 400, detail = "Network is already read")
    return {"scanned" : crud.read_network(db, network = db_network)}



@app.put("/networks/{network_id}")
def update_network(network_id: str, network_update: schemas.NetworkUpdate, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    
    return {"updated": crud.update_network(db = db, network = db_network, network_update = network_update)}



@app.delete("/networks/{network_id}")
def delete_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    return {"deleted": crud.delete_network(db, network = db_network)}




@app.get("/networks/{network_id}/data", response_model = schemas.Network)
def get_network(network_id: str, db: Session = Depends(get_db)):
    
    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code = 404, detail = "Network not found")
    return db_network

