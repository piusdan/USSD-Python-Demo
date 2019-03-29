import os
from app import create_app
from app.celery_cfg import celery
import logging

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
logging.info("creating app with config {}".format(os.environ.get('FLASK_CONFIG'), 'default'))
app.app_context().push()