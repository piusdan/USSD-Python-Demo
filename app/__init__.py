import os

from dotenv import load_dotenv
from flask import Flask

dotenv_path = os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".env")
load_dotenv(dotenv_path)

from AfricasTalkingGateway import gateway
from database import db, redis
from config import config
from celery import Celery

import logging
import logging.config
import os
import yaml

from config import Config
from celery.utils.log import get_task_logger

from flask_login import LoginManager

version__ = "0.2.0"

__author__ = "npiusdan@gmail.com"
__description__ = "Nerds Microfinance application"
__email__ = "npiusdan@gmail.com"
__copyright__ = "MIT LICENCE"


login_manager = LoginManager()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
celery_logger = get_task_logger(__name__)

def create_app(config_name):
    app = Flask(__name__)
    # configure application
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # setup login manager
    login_manager.init_app(app)
    
    # setup database
    redis.init_app(app)
    db.init_app(app)
    
    # setup celery
    celery.conf.update(app.config)
    
    # initialize africastalking gateway
    gateway.init_app(app=app)

    # register blueprints
    from app.ussd import ussd as ussd_bp
    app.register_blueprint(ussd_bp)

    # setup logging
    from app.util import setup_logging
    from config import basepath
    if app.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    path = os.path.abspath(basepath, file_name))
    setup_logging(default_level=logging_level, logger_file_path=path)

    return app
