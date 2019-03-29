
from celery import Celery

from config import Config
from celery.utils.log import get_task_logger

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

celery_logger = get_task_logger(__name__)