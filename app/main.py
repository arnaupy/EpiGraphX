"""
Main file where all the FastAPI requests are build:
|
|   NAME -> main.py
|
|   DESCRIPTION ->
|       
|    
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .routers import files, networks

from .model import schemas
from app import __version__


app = FastAPI(
    version = __version__
)

app.include_router(files.router)
app.include_router(networks.router)


@app.exception_handler(schemas.NetworkOriginError)
async def network_origin_error__handler(request: Request, exc: schemas.NetworkOriginError):
    return JSONResponse(
        status_code = 400,
        content = {"message": str(exc)}
    )

