from django.db import models
from django.contrib.auth import get_user_model

from .permissions import Permissions

User = get_user_model()


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
            (Permissions.VIEW_PROJECT, "View Project"),
            (Permissions.UPDATE_PROJECT, "Update Project"),
            (Permissions.DELETE_PROJECT, "Delete Project"),
        )

    def __str__(self):
        return self.name
