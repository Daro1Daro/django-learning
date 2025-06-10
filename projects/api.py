from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from ninja import Router, Schema, Query, FilterSchema, Field
from typing import List, Optional
from datetime import datetime
from pydantic import FutureDatetime

from .queries import query_get_user_projects, query_get_project, query_get_task
from .commands import (
    command_create_project,
    command_update_project,
    command_delete_project,
    command_create_task,
    command_update_task,
    command_delete_task,
)
from .models import StatusChoice

router = Router()


class ProjectInput(Schema):
    name: str = Field(max_length=255)
    member_ids: List[int]


class TaskInput(Schema):
    title: str = Field(max_length=255)
    description: str = Field(max_length=10000)
    status: StatusChoice
    assignee_id: Optional[int]
    due_date: Optional[FutureDatetime]


class UserOutput(Schema):
    id: int
    email: str


class ProjectOutput(Schema):
    id: int
    name: str
    owner_id: int
    members: List[UserOutput]
    created_at: datetime


class TaskOutput(Schema):
    id: int
    title: str
    description: str
    status: StatusChoice
    assignee: Optional[UserOutput]
    due_date: Optional[datetime]
    created_by: UserOutput
    created_at: datetime


class ProjectFilterSchema(FilterSchema):
    name: Optional[str] = Field(None, q="name__icontains")
    owner_email: Optional[str] = Field(None, q="owner__email__icontains")
    member_email: Optional[str] = Field(None, q="members__email__icontains")


@router.get("/", response=List[ProjectOutput])
def get_projects(request: HttpRequest, filters: ProjectFilterSchema = Query(...)):
    user = request.auth["user"]

    if not request.GET:
        projects = query_get_user_projects(user=user)
    else:
        projects = filters.filter(query_get_user_projects(user=user))

    return list(projects)


@router.get("/{id}", url_name="get_project", response=ProjectOutput)
def get_project(request: HttpRequest, id: int):
    user = request.auth["user"]
    return query_get_project(user=user, project_id=id)


@router.post("/", response={201: ProjectOutput})
def create_project(request: HttpRequest, response: HttpResponse, payload: ProjectInput):
    user = request.auth["user"]
    project = command_create_project(user=user, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return 201, project


@router.patch("/{id}", response=ProjectOutput)
def update_project(
    request: HttpRequest, response: HttpResponse, id: int, payload: ProjectInput
):
    user = request.auth["user"]
    project = command_update_project(user=user, project_id=id, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return project


@router.delete("/{id}", response={204: None})
def delete_project(request: HttpRequest, response: HttpResponse, id: int):
    user = request.auth["user"]
    command_delete_project(user=user, project_id=id)

    return 204, None


@router.get("/tasks/{task_id}", url_name="get_task", response=TaskOutput)
def get_task(request: HttpRequest, task_id: int):
    user = request.auth["user"]
    return query_get_task(user=user, task_id=task_id)


@router.post("/{project_id}/tasks", response={201: TaskOutput})
def create_task(
    request: HttpRequest, response: HttpResponse, project_id: int, payload: TaskInput
):
    user = request.auth["user"]
    task = command_create_task(user=user, project_id=project_id, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_task", args=[task.id])
    )

    return 201, task


@router.patch("/tasks/{task_id}", response=TaskOutput)
def update_task(
    request: HttpRequest,
    response: HttpResponse,
    task_id: int,
    payload: TaskInput,
):
    user = request.auth["user"]
    task = command_update_task(user=user, task_id=task_id, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_task", args=[task.id])
    )

    return task


@router.delete("/tasks/{task_id}", response={204: None})
def delete_task(request: HttpRequest, response: HttpResponse, task_id: int):
    user = request.auth["user"]
    command_delete_task(user=user, task_id=task_id)

    return 204, None
