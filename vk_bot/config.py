from os import getenv
from pathlib import Path


class Config:
    DEBUG = False
    LOCALE_DIR = Path(__file__).parent.parent.joinpath('locales')
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    REDIS_PASSWORD = getenv('REDIS_PASSWORD')

    DB_USER = getenv('POSTGRES_USER')
    DB_PASSWORD = getenv('POSTGRES_PASSWORD')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/bill_sharing'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    VK_TOKEN = getenv('VK_TOKEN')
    VK_GROUP_ID = 183589632
    VK_CONFIRMATION_STRING = getenv('VK_CONFIRMATION_STRING')
    VK_API_VERSION = '5.95'
