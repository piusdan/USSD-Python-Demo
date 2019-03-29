import os

from dotenv import load_dotenv
from flask import Flask

dotenv_path = os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".env")
load_dotenv(dotenv_path)

from app.AfricasTalkingGateway import africastalkinggateway
from app.database import db
from app.celery_cfg import celery
from config import config
from app.login_manager import login_manager
from app.redis import redis

version__ = "0.2.0"

__author__ = "npiusdan@gmail.com"
__description__ = "USSD Airtime Client"
__email__ = "npiusdan@gmail.com"
__copyright__ = "Copyright 2019 Pius Dan Nyongesa"


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    print(app.config["REDIS_URL"])

    config[config_name].init_app(app)
    login_manager.init_app(app)
    redis.init_app(app)

    db.init_app(app)

    celery.conf.update(app.config)
    africastalkinggateway.init_app(app=app)

    # register blueprints
    from app.apiv2 import api_v2 as apiv2_blueprint

    app.register_blueprint(apiv2_blueprint)

    return app
