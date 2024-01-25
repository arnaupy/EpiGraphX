from uuid import uuid4
from datetime import datetime

from app.config import postgres_settings


def get_random_id() -> str:
    return str(uuid4())


def now() -> str:
    return datetime.now().strftime(postgres_settings.datetime_format)
