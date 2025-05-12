from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Project


def get_user_projects(uid: int):
    return Project.objects.filter(Q(owner__id=uid) | Q(members__id=uid)).distinct()


def get_project_by_id(id: int):
    return get_object_or_404(Project, id=id)
