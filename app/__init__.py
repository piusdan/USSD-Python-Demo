from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    # attach routes and custom pages here

    from apiv1 import api_v1 as api10_blueprint
    app.register_blueprint(api10_blueprint, url_prefix='/api/v1.0')

    from apiv2 import api_v11 as api11_blueprint
    app.register_blueprint(api11_blueprint, url_prefix='/api/v1.1')

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    return app