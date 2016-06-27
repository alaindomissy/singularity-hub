from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shub.settings')
shubcelery = Celery('shub')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
shubcelery.config_from_object('django.conf:settings')
shubcelery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
