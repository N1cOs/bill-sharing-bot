from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from vk_api import VkApi

from vk_bot.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

vk = VkApi(token=Config.VK_API_VERSION, api_version=Config.VK_API_VERSION)
