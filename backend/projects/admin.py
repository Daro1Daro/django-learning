from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Project, Task, TaskAttachment


@admin.register(Project)
class ProjectAdmin(GuardedModelAdmin):
    list_display = ("name", "owner", "created_at", "id")
    search_fields = ("name", "owner__username", "members__username")
    list_filter = ("created_at",)
    filter_horizontal = ("members",)


@admin.register(Task)
class TaskAdmin(GuardedModelAdmin):
    list_display = (
        "title",
        "project",
        "assignee",
        "status",
        "due_date",
        "created_by",
        "created_at",
        "id",
    )
    list_filter = ("status", "project", "assignee", "created_by", "due_date")
    search_fields = (
        "title",
        "description",
        "assignee__username",
        "project__name",
        "created_by__username",
    )
    ordering = ("-created_at",)


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(GuardedModelAdmin):
    list_display = (
        "task",
        "uploaded_at",
        "id",
    )
    list_filter = ("task", "uploaded_at")
    search_fields = (
        "task__title",
        "task__project__nameuploaded_at",
    )
    ordering = ("-uploaded_at",)
