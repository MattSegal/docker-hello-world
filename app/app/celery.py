import os
from celery import Celery
from celery.utils.log import get_task_logger
from django.conf import settings


celery_host = os.environ.get('CELERY_HOST')
app = Celery('reddit', broker='amqp://' + celery_host)
app.config_from_object('django.conf:settings', namespace='CELERY')

logging = get_task_logger(__name__)
