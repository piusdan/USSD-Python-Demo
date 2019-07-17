import os

from app import celery, create_app

app = create_app(os.getenv('USSD_CONFIG') or 'default')
app.app_context().push()
