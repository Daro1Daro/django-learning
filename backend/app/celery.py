import os

from celery import Celery
import configurations

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

configurations.setup()

app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
