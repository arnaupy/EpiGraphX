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
    title = "EpiGraphX",
    summary = "☣️ App to simulate Epidemics on Networks.",
    version = __version__,
    contact={
        "name": "Arnau Perez",
        "url": "https://www.linkedin.com/in/arnau-perez-perez/",
        "email": "01arnauperez@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/arnaupy/EpiGraphX/blob/main/LICENSE",
    },
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

