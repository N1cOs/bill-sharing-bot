from os import getenv


class Config:
    DEBUG = False

    DB_USER = getenv('POSTGRES_USER')
    DB_PASSWORD = getenv('POSTGRES_PASSWORD')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/bill_sharing'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

