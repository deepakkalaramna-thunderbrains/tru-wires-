from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wireform.settings')

app = Celery('wireform')
app.conf.enable_utc = False

app.conf.update(timezone = 'US/Eastern')

app.config_from_object(settings, namespace='CELERY')


app.conf.beat_schedule = {
    'create-orders-from-recurrence': {
        'task': 'formpage.tasks.create_recurring_orders',
        'schedule': crontab(hour=17, minute=40),
        'args': (),
    },
}


app.autodiscover_tasks()

