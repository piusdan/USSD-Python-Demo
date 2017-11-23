#usr/bin/python
"""
Configuration for the USSD application
"""
import os
import logging

from raven.contrib.flask import Sentry

basedir = os.path.abspath(os.path.dirname(__file__))  # base directory

class Config:
    """General configuration variables"""

    DEBUG = False
    TESTING = False
    SECRET_KEY = b"I\xf9\x9cF\x1e\x04\xe6\xfaF\x8f\xe6)-\xa432"
    CSRF_ENABLED = True
    ADMIN_PHONENUMBER = os.environ.get('ADMIN_PHONENUMBER') or '+254703554404'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    APP_MAIL_SUBJECT_PREFIX = '[BEST LIFE SUPERMARKET]'
    APP_MAIL_SENDER = ''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SSL_DISABLE = True
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    AT_USERNAME = os.environ.get('AT_USERNAME') or 'sandbox'
    AT_APIKEY = os.environ.get('AT_APIKEY') or 'a2d657d8fc96024a22bd35a58ca87ad8db30a5edf14a136c6e1d5cd67c0dfa65'
    AT_ENVIRONMENT = os.environ.get('AT_ENVIRONMENT') or 'sandbox'

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
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        logging.basicConfig(level=logging.DEBUG)


class ProductionConfig(Config):
    """Production Mode configuration"""
    CSRF_ENABLED = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        sentry = Sentry(
            dsn="https://a88a0c9e894a45bc8a6c3ad872d22c2e:"
                "f5dcef4d47544b62a68b0d0501235366@sentry.io/227387")
        sentry.init_app(app, logging=True)


class HerokuConfig(Config):
    """Configuration specific to the Heroku platform"""
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app=app)

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
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}