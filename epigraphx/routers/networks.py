"""
Interact with network data

    NAME -> networks.py

    DESCRIPTION -> TODO
       
    FUNCTIONS: TODO
    |
    +
"""
from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.processors import file_processor
from ..core.schemas import network_schemas
from ..core.models import network_models
from ..core.features import crud
from ..databases.postgresql import get_db
from ..databases.miniodb import get_minio_db, MinioSession
from ..config.__tags import Tags

router = APIRouter(prefix="/networks", tags=[Tags.NETWORKS])


@router.post("/", response_model=network_schemas.Network)
def create_network(
    network: network_schemas.NetworkCreate, db: Session = Depends(get_db)
):
    """Registers a **Network** object in the database"""

    # Checks if 'Network label' is not already in use
    db_network = crud.pull_network_by_label(db=db, network_label=network.label)
    if db_network:
        raise HTTPException(status_code=400, detail="Network label is already in use")
    return crud.create_network(db=db, network=network)


@router.get("/")
def get_networks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    features: list[str] = Query(default=None),
):
    """Retrieves a **list of Network** objects from the database or specified features"""

    # Checks if features requested are attributes of 'Network' class
    if features:
        for feature in features:
            if feature not in network_models.Network.__dict__:
                raise HTTPException(
                    status_code=400,
                    detail=f"Feature '{feature}' not in '{network_models.Network.__name__}' attributes",
                )

    # Get a list of networks from the database
    db_networks = crud.pull_networks(db, skip=skip, limit=limit)

    return crud.describe_network(*db_networks, features=features)


@router.get("/{network_id}")
def get_network(
    network_id: str,
    db: Session = Depends(get_db),
    features: list[str] = Query(default=None),
):
    """Retrieves a **Network** object from the database or specified features"""

    # Checks if features requested are attributes of 'Network' class
    if features:
        for feature in features:
            if feature not in network_models.Network.__dict__:
                raise HTTPException(
                    status_code=400,
                    detail=f"Feature '{feature}' not in '{network_models.Network.__name__}' attributes",
                )

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id=network_id)
    if not db_network:
        raise HTTPException(status_code=404, detail="Network not found")

    return crud.describe_network(db_network, features=features)


@router.patch("/{network_id}")
def scan_network(
    network_id: str,
    db: Session = Depends(get_db),
    minio_db: MinioSession = Depends(get_minio_db),
):
    """Read the **Network**, storing its data in the database"""

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id=network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")

    # Checks if 'Network' is already read
    elif db_network.is_scanned == True:
        raise HTTPException(status_code=400, detail="Network is already scanned")

    # Checks that the network file is abailable to read
    processor = file_processor.get_file_processor(
        uploaded=True, file_class=file_processor.NetworkFile, minio_db=minio_db
    )

    # Checks that the file is abailable
    network_file = processor.pull(filename=db_network.origin)
    if not network_file:
        raise HTTPException(status_code=404, detail=f"Network file not found")

    return {
        "scanned": crud.scan_network(db, network=db_network, network_file=network_file)
    }


@router.put("/{network_id}")
def update_network(
    network_id: str,
    network_update: network_schemas.NetworkUpdate,
    db: Session = Depends(get_db),
):
    """Updates some the abailable **Network** features to update"""

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id=network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")

    # Check if `network label` is already in use
    if network_update.label:
        if crud.pull_network_by_label(db, network_label=network_update.label) and (
            network_update.label != db_network.label
        ):
            raise HTTPException(
                status_code=404, detail="Network label is already in use"
            )

    return {
        "updates": crud.update_network(
            db=db, network=db_network, network_update=network_update
        )
    }


@router.delete("/{network_id}")
def delete_network(network_id: str, db: Session = Depends(get_db)):
    """Removes a **Network** object from the database"""

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id=network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return {"deleted": crud.delete_network(db, network=db_network)}


@router.get("/{network_id}/data", response_model=network_schemas.Network)
def get_network(network_id: str, db: Session = Depends(get_db)):
    """Retrieves a **Network** object in extended form from the database"""

    # Checks if 'Network id' is registered in the database
    db_network = crud.pull_network(db, network_id=network_id)
    if db_network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return db_network
