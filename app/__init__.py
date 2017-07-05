from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from celery import Celery

from config import config, Config


db = SQLAlchemy()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    celery.conf.update(app.config)

    # register blueprints

    from apiv1 import api_v1 as api10_blueprint
    app.register_blueprint(api10_blueprint, url_prefix='/api/v1.0')

    from apiv2 import api_v11 as api11_blueprint
    app.register_blueprint(api11_blueprint, url_prefix='/api/v1.1')


    return app
