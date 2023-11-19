from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager
import os

load_dotenv("./connection/credentials.env")
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
port = os.environ['POSTGRES_PORT']
database = os.environ['POSTGRES_DB']

Database_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(Database_URL, echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

@contextmanager
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()