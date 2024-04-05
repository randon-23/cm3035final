#Celery configuration file
import os
import time

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')

redis_url =os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

app=Celery('elearning', broker=redis_url, backend=redis_url)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()