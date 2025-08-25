import django.db.models.deletion
import permissions.permissions
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "members",
                    models.ManyToManyField(
                        blank=True, related_name="projects", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="created_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "permissions": (
                    (permissions.permissions.Permissions["VIEW"], "View Project"),
                    (permissions.permissions.Permissions["UPDATE"], "Update Project"),
                    (permissions.permissions.Permissions["DELETE"], "Delete Project"),
                    (
                        permissions.permissions.Permissions["MANAGE_TASKS"],
                        "Manage Tasks",
                    ),
                ),
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "description",
                    models.TextField(blank=True, max_length=10000, null=True),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (1, "To do"),
                            (2, "In progress"),
                            (3, "Review"),
                            (4, "Done"),
                        ],
                        default=1,
                    ),
                ),
                ("due_date", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("pending_notification_sent", models.BooleanField(default=False)),
                ("overdue_notification_sent", models.BooleanField(default=False)),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="created_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="projects.project",
                    ),
                ),
            ],
            options={
                "permissions": (
                    (permissions.permissions.Permissions["VIEW"], "View Task"),
                    (permissions.permissions.Permissions["UPDATE"], "Update Task"),
                    (permissions.permissions.Permissions["DELETE"], "Delete Task"),
                ),
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="TaskAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="task_attachments/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="projects.task",
                    ),
                ),
            ],
        ),
    ]
