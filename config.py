#usr/bin/python
"""
Configuration for the USSD application
"""
import os
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))  # base directory


class Config:
    """
    General configuration variables
    """

    SECRET_KEY = os.environ.get('SECRETE_KEY') or str(uuid.uuid4())
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    AT_APIKEY = os.environ.get('AT_APIKEY') or 'bb3c6b7bfa67657485eb14f77e0935c9dfd3559f62c0542eab165079c75ea783'
    AT_USERNAME = os.environ.get('AT_USERNAME') or 'darklotus'
    AT_NUMBER = os.environ.get('AT_NUMBER') or '+254711082632'
    SMS_CODE = os.environ.get('AT_SMSCODE') or ''
    PRODUCT_NAME = os.environ.get('AT_PRODUCTNAME') or 'tus'
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Configuration variables when in development mode
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


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
    'default': DevelopmentConfig

}