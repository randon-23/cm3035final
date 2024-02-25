#Celery configuration file
import os
import time

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')

app=Celery('elearning', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()