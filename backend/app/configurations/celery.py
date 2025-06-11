from os import getenv


class CeleryConfig:
    CELERY_BROKER_URL = getenv("CELERY_BROKER", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = getenv("CELERY_BACKEND", "redis://127.0.0.1:6379/0")
