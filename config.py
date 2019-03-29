#usr/bin/python
"""
Configuration for the USSD application
"""
import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))  # base directory

class Config:
    """General configuration variables"""

    DEBUG = False
    TESTING = False
    SECRET_KEY = b"I\xf9\x9cF\x1e\x04\xe6\xfaF\x8f\xe6)-\xa432"
    CSRF_ENABLED = True
    ADMIN_PHONENUMBER = os.getenv('ADMIN_PHONENUMBER')
    CELERY_BROKER_URL = os.getenv('REDIS_URL')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    AT_USERNAME = os.getenv('AT_USERNAME')
    AT_APIKEY = os.getenv('AT_APIKEY')
    SQLALCHEMY_DATABASE_URI = "postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}".format(
        db_user=os.getenv("DB_USER", "nerdy"),
        db_name=os.getenv("DB_NAME", "nerds_micorfinance"),
        db_password=os.getenv("DB_PASSWORD", "n3rdy"),
        db_host=os.getenv("DB_HOST", "localhost")
    )
    AT_ENVIRONMENT = os.getenv('AT_ENVIRONMENT')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    APP_NAME = 'nerds-microfinance-app'

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables when in development mode
    """
    """Development Mode configuration"""
    DEBUG = True
    CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        logging.basicConfig(level=logging.DEBUG)


class ProductionConfig(Config):
    """Production Mode configuration"""
    CSRF_ENABLED = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # handle proxy server errors
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))


class TestingConfig(Config):
    """
    Testing configuration variables
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}