"""
PostgreSQL database:

    NAME -> postgresql.py

    DESCRIPTION -> This file implement the database connection from the library 'SQLAlchemy'.
       
    FUNCTIONS:
    |
    |   get_db -> return a `Session` object instance and closes the session when needed
    |       
    |       inputs: None
    |       output: <Session>
    +
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os


# Instanciate database connection parameters
database_key = os.environ.get("POSTGRES_PASSWORD")
database_name = os.environ.get("POSTGRES_DB_NAME")
host_name = os.environ.get("POSTGRES_HOST")
user_name = os.environ.get("POSTGRES_USER")
port_number = os.environ.get("POSTGRES_PORT")

# Build database conncetion url
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{user_name}:{database_key}@{host_name}:{port_number}/{database_name}"
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
