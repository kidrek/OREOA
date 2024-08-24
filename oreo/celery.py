# OreO/celery.py
from __future__ import absolute_import, unicode_literals
import logging, os

from celery import Celery
from oreo import settings


app = Celery('Oreo')
app.config_from_object('oreo:settings', namespace='CELERY')
app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task(name='debug', bind=True)
def debug_task(self):
    logging.info(f'Task : Call Debug')

