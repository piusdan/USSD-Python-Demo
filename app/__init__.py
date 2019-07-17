import logging
import logging.config
import os

from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from config import config, Config
from .AfricasTalkingGateway import gateway
from .database import db, redis

dotenv_path = os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".env")
load_dotenv(dotenv_path)

__version__ = "0.2.0"
__author__ = "npiusdan@gmail.com"
__description__ = "Nerds Microfinance application"
__email__ = "npiusdan@gmail.com"
__copyright__ = "MIT LICENCE"

login_manager = LoginManager()

celery_logger = get_task_logger(__name__)


def create_celery():
    from celery import Celery

    celery = Celery(
        __name__,
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )
    return celery


celery = create_celery()


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

    # initialize africastalking gateway
    gateway.init_app(app=app)

    # setup celery
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # register blueprints
    from app.ussd import ussd as ussd_bp

    app.register_blueprint(ussd_bp)

    # setup logging
    from app.util import setup_logging
    from config import basedir

    if app.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    path = os.path.join(basedir, "app_logger.yaml")
    setup_logging(default_level=logging_level, logger_file_path=path)
    return app
