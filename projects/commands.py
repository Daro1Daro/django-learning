from typing import Optional
from guardian.shortcuts import assign_perm
from datetime import datetime


from users.models import User
from users.queries import query_get_user_by_id
from permissions.permissions import (
    Permissions,
    assign_standard_permissions,
    assign_project_member_permissions,
    remove_project_member_permissions,
    assign_task_assignee_permissions,
    remove_task_assignee_permissions,
)
from .models import Project, Task, StatusChoice
from .queries import query_get_project, query_get_task
from .exceptions import ProjectPermissionDenied


def command_create_project(user: User, name: str, member_ids: set[int]) -> Project:
    project: Project = Project.objects.create(owner=user, name=name)

    # TODO: check if members exist
    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)

    assign_standard_permissions(user=user, obj=project)
    assign_perm(Permissions.MANAGE_TASKS, user, project)

    for member in members:
        assign_project_member_permissions(user=member, project=project)

    return project


def command_update_project(
    user: User, project_id: int, name: str, member_ids: set[int]
) -> Project:
    project: Project = query_get_project(user=user, project_id=project_id)

    if not user.has_perm(perm=Permissions.UPDATE, obj=project):
        raise ProjectPermissionDenied

    for previous_member in project.members.exclude(
        id__in=member_ids + [project.owner.id]
    ):
        remove_project_member_permissions(user=previous_member, project=project)

    project.name = name
    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)

    for member in members:
        assign_project_member_permissions(user=member, project=project)

    project.full_clean()
    project.save()

    return project


def command_delete_project(user: User, project_id: int):
    project: Project = query_get_project(user=user, project_id=project_id)

    if not user.has_perm(perm=Permissions.DELETE, obj=project):
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

    if not (
        user.has_perm(Permissions.UPDATE, project)
        or user.has_perm(Permissions.MANAGE_TASKS, project)
    ):
        raise ProjectPermissionDenied

    task = Task(
        created_by=user,
        project=project,
        title=title,
        description=description,
        status=status,
        assignee=query_get_user_by_id(uid=assignee_id) if assignee_id else None,
        due_date=due_date,
    )

    task.full_clean()
    task.save()

    assign_standard_permissions(user=user, obj=task)

    if task.assignee and task.assignee.id != user.id:
        assign_task_assignee_permissions(task.assignee, task)

    return task


def command_update_task(
    user: User,
    task_id: int,
    title: str,
    description: str,
    status: StatusChoice,
    assignee_id: Optional[int] = None,
    due_date: Optional[datetime] = None,
) -> Task:
    task: Task = query_get_task(user=user, task_id=task_id)
    if not (
        user.has_perm(Permissions.UPDATE, task)
        or user.has_perm(Permissions.MANAGE_TASKS, task.project)
    ):
        raise ProjectPermissionDenied

    if (
        task.assignee
        and task.assignee.id != task.created_by.id
        and task.assignee.id != assignee_id
    ):
        remove_task_assignee_permissions(task.assignee)

    task.title = title
    task.description = description
    task.status = status
    task.due_date = due_date
    task.assignee = query_get_user_by_id(uid=assignee_id) if assignee_id else None

    task.full_clean()
    task.save()

    if task.assignee:
        assign_perm(Permissions.UPDATE, task.assignee, task)

    return task


def command_delete_task(user: User, task_id: int):
    task: Task = query_get_task(user=user, task_id=task_id)

    if not (
        user.has_perm(Permissions.DELETE, task)
        or user.has_perm(Permissions.MANAGE_TASKS, task.project)
    ):
        raise ProjectPermissionDenied

    task.delete()
