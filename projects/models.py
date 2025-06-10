from enum import StrEnum

from django.db import models
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
            (Permissions.CREATE_TASK, "Create Task"),
        )

    def __str__(self):
        return self.name


class Task(models.Model):
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
