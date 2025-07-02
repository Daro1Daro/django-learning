from enum import StrEnum
from datetime import timedelta

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from permissions.permissions import Permissions

User = get_user_model()


class StatusChoice(StrEnum):
    TO_DO = "TD"
    IN_PROGRESS = "IP"
    REVIEW = "RE"
    DONE = "DN"


class Project(models.Model):
    name = models.CharField(max_length=255, blank=False)
    owner = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_projects"
    )
    members = models.ManyToManyField(User, related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_permissions = ()
        permissions = (
            (Permissions.VIEW, "View Project"),
            (Permissions.UPDATE, "Update Project"),
            (Permissions.DELETE, "Delete Project"),
            (Permissions.MANAGE_TASKS, "Manage Tasks"),
        )

    def __str__(self):
        return self.name


class TaskReadModel(QuerySet):
    def get_pending(self: QuerySet["Task"]) -> QuerySet["Task"]:
        soon = now() + timedelta(hours=1)
        return self.filter(
            due_date__lte=soon,
            due_date__gte=now(),
        ).exclude(status=StatusChoice.DONE)

    def get_overdue(self: QuerySet["Task"]) -> QuerySet["Task"]:
        return self.filter(due_date__lte=now()).exclude(status=StatusChoice.DONE)


class Task(models.Model):
    objects = models.Manager()
    read_model = TaskReadModel.as_manager()

    STATUS_CHOICES = {
        StatusChoice.TO_DO: "TO DO",
        StatusChoice.IN_PROGRESS: "IN PROGRESS",
        StatusChoice.REVIEW: "REVIEW",
        StatusChoice.DONE: "DONE",
    }

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=10000, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=StatusChoice.TO_DO,
    )
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="created_tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    pending_notification_sent = models.BooleanField(default=False)
    overdue_notification_sent = models.BooleanField(default=False)

    class Meta:
        default_permissions = ()
        permissions = (
            (Permissions.VIEW, "View Task"),
            (Permissions.UPDATE, "Update Task"),
            (Permissions.DELETE, "Delete Task"),
        )

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.due_date and self.due_date <= now():
            raise ValidationError({"due_date": "Due date must be in the future."})


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="task_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split("/")[-1]
