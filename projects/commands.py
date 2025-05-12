from typing import List
from django.shortcuts import get_object_or_404


from users.models import User
from .models import Project


def command_create_project(uid: int, name: str, member_ids: List[int]) -> Project:
    owner = get_object_or_404(User, id=uid)
    project = Project.objects.create(owner=owner, name=name)

    if member_ids:
        members = User.objects.filter(id__in=member_ids)
        project.members.set(members)

    return project
