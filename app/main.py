"""
Main file where all the FastAPI requests are build:
|
|   NAME -> main.py
|
|   DESCRIPTION -> TODO
|       
|    
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .routers import files, networks
from .core.schemas import network_schemas
from app import __version__

# Instanciate FastAPI app
app = FastAPI(
    version = __version__
)

# Add routers
app.include_router(files.router)
app.include_router(networks.router)


@app.exception_handler(network_schemas.NetworkOriginError)
async def network_origin_error__handler(request: Request, exc: network_schemas.NetworkOriginError):
    return JSONResponse(
        status_code = 400,
        content = {"message": str(exc)}
    )

