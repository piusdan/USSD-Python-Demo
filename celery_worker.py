import os

from app import create_app, celery

app = create_app(os.getenv('USSD_CONFIG') or 'default')
app.app_context().push()
