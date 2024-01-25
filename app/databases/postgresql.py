"""
PostgreSQL database:

    NAME -> postgresql.py

    DESCRIPTION -> This file implements a database connection using 'SQLAlchemy'.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import postgres_settings


# Build database conncetion url
SQLALCHEMY_DATABASE_URL = "postgresql://{user_name}:{database_key}@{host_name}:{port_number}/{database_name}".format(
    user_name=postgres_settings.postgres_user,
    database_key=postgres_settings.postgres_password,
    host_name=postgres_settings.postgres_host,
    port_number=postgres_settings.postgres_port,
    database_name=postgres_settings.postgres_db_name,
)

# Instanciate the SQLAlchemy engine to make requests and a session class for this connection
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Returns the database Session object to make requests"""

    db = Session()
    try:
        yield db
    finally:
        db.close()
