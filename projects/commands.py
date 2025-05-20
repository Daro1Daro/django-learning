from typing import List
from guardian.shortcuts import assign_perm


from users.models import User
from .models import Project
from .queries import query_get_project
from .permissions import Permissions
from .exceptions import ProjectPermissionDenied


def command_create_project(user: User, name: str, member_ids: List[int]) -> Project:
    project: Project = Project.objects.create(owner=user, name=name)

    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)

    assign_perm(Permissions.DELETE_PROJECT, user, project)
    assign_perm(Permissions.VIEW_PROJECT, user, project)
    assign_perm(Permissions.UPDATE_PROJECT, user, project)

    for member in members:
        assign_perm(Permissions.VIEW_PROJECT, member, project)

    return project


def command_update_project(
    user: User, project_id: int, name: str, member_ids: List[int]
) -> Project:
    project: Project = query_get_project(uid=user.id, id=project_id)

    if not user.has_perm(Permissions.UPDATE_PROJECT, project):
        raise ProjectPermissionDenied

    project.name = name
    members = User.objects.filter(id__in=member_ids)
    project.members.set(members)
    for member in members:
        assign_perm(Permissions.VIEW_PROJECT, member, project)

    project.save()

    return project
