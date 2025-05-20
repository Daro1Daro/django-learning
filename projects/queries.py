from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user

from users.models import User
from .models import Project
from .exceptions import ProjectPermissionDenied
from .permissions import Permissions


def query_get_user_projects(user: User):
    # return Project.objects.filter(Q(owner__id=uid) | Q(members__id=uid)).distinct()
    return get_objects_for_user(
        user=user, perms=Permissions.VIEW_PROJECT, klass=Project, with_superuser=True
    )


def query_get_project(user: User, project_id: int) -> Project:
    project: Project = get_object_or_404(Project, id=project_id)

    if not user.has_perm(Permissions.VIEW_PROJECT, project):
        raise ProjectPermissionDenied

    return project
