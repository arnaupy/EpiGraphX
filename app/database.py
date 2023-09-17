from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

try:
    database_key = os.environ["POSTGRES_PASSWORD"]
    database_name = os.environ["POSTGRES_DB_NAME"]
    host_name = os.environ["POSTGRES_HOST"]
    user_name = os.environ["POSTGRES_USER"]
    port_number = os.environ["POSTGRES_PORT"]

    SQLALCHEMY_DATABASE_URL = f"postgresql://{user_name}:{database_key}@{host_name}:{port_number}/{database_name}"

    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo = False)
    SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

except:
    raise NotImplementedError

Base = declarative_base()
