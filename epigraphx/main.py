"""
Main file where all the FastAPI requests are build:
|
|   NAME -> main.py
|
|   DESCRIPTION -> TODO
|       
|    
"""
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from .routers import files, networks, logs
from .core.models import network_models, file_models
from .databases.postgresql import engine
from .databases.miniodb import minio_client, MINIO_BUCKET_NAME
from .config.__metadata import metadata
from .middleware import log_middleware
from .logger import logger

from .core.exceptions import NetworkOriginError
from .exception_handlers import network_origin_error__handler

# Write the app documentation description
description = """
## Files

Files are stored in a **minio** bucket.

## Networks

Networks are stored in a **postgres** database.
"""

# Instanciate FastAPI app
app = FastAPI(
    title=metadata.get("name"),
    summary=metadata.get("description"),
    description=description,
    version=metadata.get("version"),
    contact={"name": metadata.get("author"), "email": metadata.get("author_email")},
    license_info={"name": metadata.get("license")},
)

# Add middleware for logs
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

# ------------------------------------| Add routers |------------------------------------
app.include_router(files.router)
app.include_router(networks.router)
app.include_router(logs.router)

# --------------------------| Build postgres databases tables |--------------------------
network_models.Base.metadata.create_all(bind=engine)

# --------------------------------| Build minio bucket |---------------------------------
file_models.FileBase.create_all(minio_client, MINIO_BUCKET_NAME)

# ---------------------------| Add custom exception handlers |---------------------------
app.add_exception_handler(NetworkOriginError, handler=network_origin_error__handler)

logger.info("Starting API...")


