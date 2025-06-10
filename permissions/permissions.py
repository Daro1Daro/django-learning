from enum import StrEnum

from guardian.shortcuts import assign_perm, remove_perm

from users.models import User


class Permissions(StrEnum):
    DELETE = "delete"
    UPDATE = "change"
    VIEW = "view"
    MANAGE_TASKS = "manage_tasks"


def assign_standard_permissions(user: User, obj):
    assign_perm(Permissions.VIEW, user, obj)
    assign_perm(Permissions.DELETE, user, obj)
    assign_perm(Permissions.UPDATE, user, obj)


def remove_standard_permissions(user: User, obj):
    remove_perm(Permissions.VIEW, user, obj)
    remove_perm(Permissions.DELETE, user, obj)
    remove_perm(Permissions.UPDATE, user, obj)


def assign_project_member_permissions(user: User, project: "Project"):
    assign_perm(Permissions.VIEW, user, project)
    assign_perm(Permissions.MANAGE_TASKS, user, project)


def remove_project_member_permissions(user: User, project: "Project"):
    remove_perm(Permissions.VIEW, user, project)
    remove_perm(Permissions.MANAGE_TASKS, user, project)


def assign_task_assignee_permissions(assignee: User, task: "Task"):
    assign_perm(Permissions.VIEW, assignee, task)
    assign_perm(Permissions.UPDATE, assignee, task)


def remove_task_assignee_permissions(assignee: User, task: "Task"):
    remove_perm(Permissions.VIEW, assignee, task)
    remove_perm(Permissions.UPDATE, assignee, task)
