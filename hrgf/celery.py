import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hrgf.settings")

app = Celery("hrgf")
app.conf.worker_name = "worker1@hostname"

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
