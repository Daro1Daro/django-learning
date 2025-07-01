from os import getenv

from celery.schedules import crontab


class CeleryConfig:
    CELERY_BROKER_URL = getenv("CELERY_BROKER", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = getenv("CELERY_BACKEND", "redis://127.0.0.1:6379/0")
    CELERY_TIMEZONE = "Europe/Warsaw"

    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
    CELERY_BEAT_SCHEDULE = {
        "send_email_for_overdue_tasks": {
            "task": "projects.tasks.send_email_for_overdue_tasks",
            "schedule": crontab(minute="*/1"),
        },
        "send_email_for_pending_tasks": {
            "task": "projects.tasks.send_email_for_pending_tasks",
            "schedule": crontab(minute="*/1"),
        },
    }
