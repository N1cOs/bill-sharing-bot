import gettext
import logging
from sys import stdout

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from vk_api import VkApi

from vk_bot.config import Config

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(stream=stdout, level=logging.INFO,
                    format=Config.LOG_FORMAT, datefmt=Config.DATETIME_FORMAT)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

redis = Redis(password=Config.REDIS_PASSWORD)

ru = gettext.translation('msg', localedir=Config.LOCALE_DIR, languages=['ru'])
ru.install()

vk = VkApi(token=Config.VK_TOKEN, api_version=Config.VK_API_VERSION)
