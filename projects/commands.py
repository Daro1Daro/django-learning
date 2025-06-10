from typing import List, Optional
from guardian.shortcuts import assign_perm
from datetime import datetime


from users.models import User
from users.queries import query_get_user_by_id
from .models import Project, Task, StatusChoice
from .queries import query_get_project
from .permissions import Permissions
from .exceptions import ProjectPermissionDenied


def command_create_project(user: User, name: str, member_ids: List[int]) -> Project:
    project: Project = Project.objects.create(owner=user, name=name)

    # TODO: check if members exist
    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)

    assign_perm(Permissions.DELETE_PROJECT, user, project)
    assign_perm(Permissions.VIEW_PROJECT, user, project)
    assign_perm(Permissions.UPDATE_PROJECT, user, project)
    assign_perm(Permissions.CREATE_TASK, user, project)

    for member in members:
        assign_perm(Permissions.VIEW_PROJECT, member, project)

    return project


def command_update_project(
    user: User, project_id: int, name: str, member_ids: List[int]
) -> Project:
    project: Project = query_get_project(user=user, project_id=project_id)

    if not user.has_perm(perm=Permissions.UPDATE_PROJECT, obj=project):
        raise ProjectPermissionDenied

    project.name = name
    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)
    for member in members:
        assign_perm(Permissions.VIEW_PROJECT, member, project)

    project.full_clean()
    project.save()

    return project


def command_delete_project(user: User, project_id: int):
    project: Project = query_get_project(user=user, project_id=project_id)

    if not user.has_perm(perm=Permissions.DELETE_PROJECT, obj=project):
        raise ProjectPermissionDenied

    project.delete()


def command_create_task(
    user: User,
    project_id: int,
    title: str,
    description: str,
    status: StatusChoice,
    assignee_id: Optional[int] = None,
    due_date: Optional[datetime] = None,
) -> Task:
    project: Project = query_get_project(user=user, project_id=project_id)

    if not user.has_perm(perm=Permissions.CREATE_TASK, obj=project):
        raise ProjectPermissionDenied

    if assignee_id:
        assignee = query_get_user_by_id(uid=assignee_id)

    task = Task(
        created_by=user,
        project=project,
        title=title,
        description=description,
        status=status,
        assignee=assignee,
        due_date=due_date,
    )

    task.full_clean()
    task.save()

    assign_perm(Permissions.DELETE_TASK, user, task)
    assign_perm(Permissions.VIEW_TASK, user, task)
    assign_perm(Permissions.UPDATE_TASK, user, task)

    if assignee:
        assign_perm(Permissions.VIEW_TASK, assignee, task)
        assign_perm(Permissions.UPDATE_TASK, assignee, task)

    return task
