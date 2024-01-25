import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process the request
        start = time.time()
        try:
            response = await call_next(request)

        # Handle unexpected errors from the server
        except Exception as e:
            logger.exception(f"({e.__class__.__name__}) {e}")

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                },
            )

        if response.status_code < 400:
            # Log successful request
            process_time = time.time() - start
            logger.info(
                {
                    "status_code": response.status_code,
                    "url": request.url.path,
                    "method": request.method,
                    "process_time": process_time,
                }
            )

        return response


async def http_exception__handler(request: Request, exc: HTTPException):
    logger.info(
        {
            "status_code": exc.status_code,
            "url": request.url.path,
            "method": request.method,
            "detail": exc.detail,
        }
    )
    return JSONResponse(
        status_code=exc.status_code, content={"message": str(exc.detail)}
    )
