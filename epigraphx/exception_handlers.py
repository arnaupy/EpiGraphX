from fastapi import Request
from fastapi.responses import JSONResponse

from .core import exceptions


async def network_origin_error__handler(
    request: Request, exc: exceptions.NetworkOriginError
):
    return JSONResponse(status_code=400, content={"message": str(exc)})
