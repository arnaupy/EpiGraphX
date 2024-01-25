from fastapi import HTTPException
from typing import Any, Optional


class CustomException(HTTPException):
    status_code: int = 418

    def __init__(
        self,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=self.__class__.status_code, detail=detail, headers=headers
        )


class InvalidFileExtension(CustomException):
    """Raises when the file name missmatches the class extention"""

    status_code: int = 400


class NetworkOriginError(CustomException):
    """Raises when the origin of a network is incorrect"""

    status_code: int = 400


class InvalidArrayStringFormat(CustomException):
    """Raises when the string format of the mapped type variable is not correct"""

    status_code: int = 500


class SizeMissmatchError(CustomException):
    """Raises when the size of the array missmatches the array length"""

    status_code: int = 500
