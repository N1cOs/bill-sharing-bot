from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import getenv

DB_USER = getenv('POSTGRES_USER')
DB_PASSWORD = getenv('POSTGRES_PASSWORD')
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/bill_sharing', echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()
