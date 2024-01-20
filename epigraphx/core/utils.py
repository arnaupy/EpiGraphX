from uuid import uuid4
from datetime import datetime

from ..config import __system


def get_random_id() -> str:
    return str(uuid4())


def now(dateformat: str = __system.DATETIME_FORMAT) -> str:
    """Return the actual string datetime according to the input format"""

    return datetime.now().strftime(__system.DATETIME_FORMAT)
