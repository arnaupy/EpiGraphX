from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

database_key = os.environ["DATABASE_KEY"]
database_name = os.environ["DATABASE_NAME"]
host_name = os.environ["HOST_NAME"]
user_name = os.environ["USER_NAME"]
port_number = os.environ["PORT_NUMBER"]

engine = create_engine(f"postgresql://{user_name}:{database_key}@{host_name}:{port_number}/{database_name}", echo = False)
Session = sessionmaker(bind=engine)

Base = declarative_base()