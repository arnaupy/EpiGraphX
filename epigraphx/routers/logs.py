from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..config.__logger import LOGS_FILENAME
from ..config.__tags import Tags


router = APIRouter(prefix="/logs", tags=[Tags.LOGS])

@router.get("/")
async def get_logs():
    with open(LOGS_FILENAME, "r") as file:
        content = file.read()
    return PlainTextResponse(content, status_code=200)