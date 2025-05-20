from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from ninja import Router, Schema, Query, FilterSchema, Field
from typing import List, Optional
from datetime import datetime

from .models import Project
from .queries import query_get_user_projects, query_get_project
from .commands import command_create_project, command_update_project

router = Router()


class ProjectInput(Schema):
    name: str = Field(max_length=255)
    member_ids: List[int]


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
    user = request.auth["user"]

    if len(request.GET.keys()) == 0:
        projects = query_get_user_projects(user=user)
    else:
        projects = filters.filter(query_get_user_projects(user=user))

    return list(projects)


@router.get("/{id}", url_name="get_project", response=ProjectOutput)
def get_project(request: HttpRequest, id: int):
    user = request.auth["user"]
    return query_get_project(user=user, project_id=id)


@router.post("/", response=ProjectOutput)
def create_project(request: HttpRequest, response: HttpResponse, payload: ProjectInput):
    user = request.auth["user"]
    project = command_create_project(user=user, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return project


@router.patch("/{id}", response=ProjectOutput)
def update_project(
    request: HttpRequest, id: int, response: HttpResponse, payload: ProjectInput
):
    user = request.auth["user"]
    project = command_update_project(user=user, project_id=id, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return project
