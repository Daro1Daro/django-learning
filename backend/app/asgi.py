import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "DEV")

from configurations.asgi import get_asgi_application

application = get_asgi_application()
