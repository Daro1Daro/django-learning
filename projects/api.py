from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from ninja import Router, Schema, Query, FilterSchema, Field
from typing import List, Optional
from datetime import datetime

from .models import Project
from .queries import get_user_projects, get_project_by_id
from .commands import command_create_project

router = Router()


class ProjectInput(Schema):
    name: str
    member_ids: Optional[List[int]] = None


class MemberOutput(Schema):
    id: int
    email: str


class ProjectOutput(Schema):
    id: int
    name: str
    owner_id: int
    members: List[MemberOutput]
    created_at: datetime


class ProjectFilterSchema(FilterSchema):
    name: Optional[str] = Field(None, q="name__icontains")
    owner_email: Optional[str] = Field(None, q="owner__email__icontains")
    member_email: Optional[str] = Field(None, q="members__email__icontains")


@router.get("/", response=List[ProjectOutput])
def get_projects(request: HttpRequest, filters: ProjectFilterSchema = Query(...)):
    uid = request.auth["payload"]["uid"]

    if len(request.GET.keys()) == 0:
        projects = get_user_projects(uid=uid)
    else:
        projects = filters.filter(Project.objects.all())

    return list(projects)


@router.get("/{id}", url_name="get_project", response=ProjectOutput)
def get_project(request: HttpRequest, id: int):
    return get_project_by_id(id=id)


@router.post("/", response=ProjectOutput)
def create_project(request: HttpRequest, response: HttpResponse, payload: ProjectInput):
    uid = request.auth["payload"]["uid"]

    project = command_create_project(uid=uid, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return project
