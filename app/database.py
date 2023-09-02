from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

database_key = os.environ["POSTGRES_PASSWORD"]
database_name = os.environ["POSTGRES_DB_NAME"]
host_name = os.environ["POSTGRES_HOSTNAME"]
user_name = os.environ["POSTGRES_USER"]
port_number = os.environ["POSTGRES_PORT"]

engine = create_engine(f"postgresql://{user_name}:{database_key}@{host_name}:{port_number}/{database_name}", echo = False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
