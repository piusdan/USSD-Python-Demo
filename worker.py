import os

from app import create_app, celery

app = create_app(os.getenv('USSD_CONFIG') or 'default')
app.app_context().push()


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask