"""
TODO

    NAME -> main.py
 
    DESCRIPTION -> TODO    
"""
from fastapi import FastAPI, HTTPException

from app.routers import files, networks, logs
from app.core.models import network_models, file_models
from app.databases.postgresql import engine
from app.databases.miniodb import minio_client, bucket_name
from app.middleware import ExceptionHandlerMiddleware, http_exception__handler
from app.logger import logger
from app.config import metadata


# Write the app documentation description
description = """
## Files

Files are stored in a **minio** bucket. It works as a local development environment database with compatibility on the cloud with **S3 AWS**.

## Networks

Networks are stored in a **postgres** database. Connections with the database are stablished using **SQLAlchemy**.
"""

# Instanciate FastAPI app
app = FastAPI(
    title=metadata.project_name,
    summary=metadata.project_description,
    description=description,
    version=metadata.version,
    contact={
        "name": metadata.author,
        "email": metadata.author_email,
        "url": metadata.contact_url,
    },
    license_info={"name": metadata.license},
    on_startup=logger.info("Starting API..."),
)

# Add middleware
app.add_middleware(ExceptionHandlerMiddleware)

# Add custom http exeption handler
app.add_exception_handler(HTTPException, http_exception__handler)

# ===================================== Add routers ====================================
app.include_router(files.router)
app.include_router(networks.router)
app.include_router(logs.router)

# ==========================| Build postgres databases tables |==========================
network_models.Base.metadata.create_all(bind=engine)

# ================================| Build minio bucket |=================================
file_models.FileBase.create_all(minio_client, bucket_name)
