from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.query import QuerySet

from .models import Task

logger = get_task_logger(__name__)


@shared_task
def send_email_for_overdue_tasks():
    logger.info("Checking for overdue tasks...")

    overdue_tasks: QuerySet[Task] = Task.read_model.get_overdue().filter(
        overdue_notification_sent=False
    )

    for task in overdue_tasks:
        # TODO: add project url when frontend is ready
        project_url = "[PROJECT_URL]"

        recipient_list = (
            [task.created_by.email, task.assignee.email]
            if task.assignee and task.assignee.id != task.created_by.id
            else [task.created_by.email]
        )

        send_mail(
            subject=f"Your task '{task.title}' has exceeded the deadline.",
            message=f"Follow this link to see the tasks: {project_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )
        task.overdue_notification_sent = True
        task.save()


@shared_task
def send_email_for_pending_tasks():
    logger.info("Checking for pending tasks...")

    pending_tasks: QuerySet[Task] = Task.read_model.get_pending().filter(
        pending_notification_sent=False
    )

    for task in pending_tasks:
        # TODO: add project url when frontend is ready
        project_url = "[PROJECT_URL]"

        recipient_list = (
            [task.created_by.email, task.assignee.email]
            if task.assignee and task.assignee.id != task.created_by.id
            else [task.created_by.email]
        )

        send_mail(
            subject=f"The deadline for your task '{task.title}' is at {task.due_date}.",
            message=f"Follow this link to see the tasks: {project_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )
        task.pending_notification_sent = True
        task.save()
