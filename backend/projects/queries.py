from typing import List

from django.shortcuts import get_object_or_404
from guardian.shortcuts import get_objects_for_user

from users.models import User
from permissions.permissions import Permissions
from .models import Project, Task
from .exceptions import ProjectPermissionDenied


def query_get_user_projects(user: User):
    # return Project.objects.filter(Q(owner__id=uid) | Q(members__id=uid)).distinct()
    return get_objects_for_user(
        user=user, perms=Permissions.VIEW, klass=Project, with_superuser=True
    )


def query_get_project(user: User, project_id: int) -> Project:
    project: Project = get_object_or_404(Project, id=project_id)

    if not user.has_perm(perm=Permissions.VIEW, obj=project):
        raise ProjectPermissionDenied

    return project


def query_get_task(user: User, task_id: int) -> Task:
    task: Task = get_object_or_404(Task, id=task_id)

    if not (
        user.has_perm(Permissions.VIEW, task)
        or user.has_perm(Permissions.VIEW, task.project)
    ):
        raise ProjectPermissionDenied

    return task


def query_get_tasks(user: User) -> List[Task]:
    return get_objects_for_user(user=user, perms=Permissions.VIEW, klass=Task)
