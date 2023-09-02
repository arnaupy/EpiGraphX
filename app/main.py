from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas, view
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/networks/", response_model = schemas.Network)
def create_network(network: schemas.NetworkCreate, db: Session = Depends(get_db)):
    db_network = crud.pull_network_by_label(db = db, label = network.label)
    if db_network:
        raise HTTPException(status_code=400, detail="Network label is already in use")
    return crud.register_network(db = db, network = network)

@app.post("/degrees/", response_model = schemas.Degree)
def create_degree(degree: schemas.DegreeCreate, db: Session = Depends(get_db)):
    db_degree = crud.pull_degree_by_attributes(db = db, 
                                 network_id = degree.network_id, 
                                 item_position = degree.item_position, 
                                 item_value = degree.item_value)
    if db_degree:
        raise HTTPException(status_code=400, detail="Link already existing")
    return crud.add_degree(db = db, degree = degree)


@app.get("/networks/", response_model=list[schemas.Network])
def get_networks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    networks = crud.pull_networks(db, skip=skip, limit=limit)
    return networks


@app.get("/networks/id", response_model=list[str])
def get_networks_id(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    networks = crud.pull_networks(db, skip=skip, limit=limit, show_id=True)
    return networks


@app.get("/networks/{network_id}", response_model=schemas.Network)
def get_network(network_id: str, db: Session = Depends(get_db)):
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return db_network


@app.get("/networks/describe/{network_id}", response_model=dict)
def get_network_description(network_id: str, db: Session = Depends(get_db)):
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return view.describe_network(network = db_network)


@app.get("/degrees/{degree_id}", response_model=schemas.Degree)
def get_degree(degree_id: str, db: Session = Depends(get_db)):
    db_degree = crud.pull_network(db, degree_id = degree_id)
    if db_degree is None:
        raise HTTPException(status_code=404, detail="Degree not found")
    return db_degree


@app.delete("/networks/{network_id}", response_model=dict)
def delete_network(network_id: str, db: Session = Depends(get_db)):
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return {"deleted": crud.remove_network(db, network = db_network)}


@app.delete("/degrees/{degree_id}", response_model=dict)
def delete_degree(degree_id: str, db: Session = Depends(get_db)):
    db_degree = crud.pull_degree(db, degree_id = degree_id)
    if db_degree is None:
        raise HTTPException(status_code=404, detail="Degree not found")
    return {"deleted": crud.remove_degree(db, degree = db_degree)}


@app.patch("/networks/{network_id}", response_model=schemas.Network)
def scan_network(network_id: str, db: Session = Depends(get_db)):
    db_network = crud.pull_network(db, network_id = network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    
    elif db_network.is_read == True:
        raise HTTPException(status_code=400, detail="Network is already read")

    return crud.read_network(db, network = db_network)


@app.get("/networks/{network_id}", response_model=schemas.Degree)
def get_degree(degree_id: str, db: Session = Depends(get_db)):
    db_degree = crud.pull_network(db, degree_id = degree_id)
    if db_degree is None:
        raise HTTPException(status_code=404, detail="Degree not found")
    return db_degree





# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
