"""
TODO

    NAME -> files.py

    DESCRIPTION -> TODO
"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.config import Tags, logs_settings


router = APIRouter(prefix="/logs", tags=[Tags.LOGS])


@router.get("/")
async def get_logs():
    with open(logs_settings.logs_filename, "r") as file:
        content = file.read()
    return PlainTextResponse(content, status_code=200)
