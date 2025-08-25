from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ValidationError
from ninja import Router, Schema, Query, FilterSchema, Field, File
from ninja.files import UploadedFile
from typing import List, Optional
from datetime import datetime
from pydantic import FutureDatetime

from . import queries
from . import commands
from .models import Task

router = Router()


ACCEPTED_TYPES = ["image/png", "image/jpeg", "application/pdf"]


def validate_task_attachment_type(file: File[UploadedFile]):
    if file.content_type not in ACCEPTED_TYPES:
        raise ValidationError(f"Unsupported file type: {file.content_type}")


class ProjectInput(Schema):
    name: str = Field(max_length=255)
    member_ids: set[int]


class TaskInput(Schema):
    title: str = Field(max_length=255)
    description: str = Field(max_length=10000)
    status: Task.StatusChoice
    assignee_id: Optional[int]
    due_date: Optional[FutureDatetime]


class UserOutput(Schema):
    id: int
    email: str


class ProjectOutput(Schema):
    id: int
    name: str
    owner_id: int
    members: list[UserOutput]
    created_at: datetime


class TaskOutput(Schema):
    id: int
    title: str
    description: str
    attachments: list[str]
    status: Task.StatusChoice
    assignee: Optional[UserOutput]
    due_date: Optional[datetime]
    created_by: UserOutput
    created_at: datetime

    @staticmethod
    def resolve_attachments(obj, context):
        request = context["request"]
        return [
            request.build_absolute_uri(attachment.file.url)
            for attachment in obj.attachments.all()
        ]


class ProjectFilterSchema(FilterSchema):
    name: Optional[str] = Field(None, q="name__icontains")
    owner_email: Optional[str] = Field(None, q="owner__email__icontains")
    member_email: Optional[str] = Field(None, q="members__email__icontains")


class TaskFilterSchema(FilterSchema):
    project_id: Optional[int] = Field(None, q="project__id__exact")
    title: Optional[str] = Field(None, q="title__icontains")
    description: Optional[str] = Field(None, q="description__icontains")
    status: Optional[Task.StatusChoice] = Field(None, q="status__iexact")
    assignee_id: Optional[int] = Field(None, q="assignee__id__exact")
    created_by_id: Optional[int] = Field(None, q="created_by__id__exact")
    due_date_gte: Optional[datetime] = Field(None, q="due_date__gte")
    due_date_lte: Optional[datetime] = Field(None, q="due_date__lte")


@router.get("/tasks", url_name="get_tasks", response=list[TaskOutput])
def get_tasks(request: HttpRequest, filters: TaskFilterSchema = Query(...)):
    user = request.auth["user"]

    tasks = (
        filters.filter(queries.get_tasks(user=user))
        if request.GET
        else queries.get_tasks(user=user)
    )

    return list(tasks)


@router.get("/tasks/{task_id}", url_name="get_task", response=TaskOutput)
def get_task(request: HttpRequest, task_id: int):
    user = request.auth["user"]
    return queries.get_task(user=user, task_id=task_id)


@router.post("/{id}/tasks", response={201: TaskOutput})
def create_task(
    request: HttpRequest,
    response: HttpResponse,
    id: int,
    payload: TaskInput,
    files: File[List[UploadedFile]] = None,
):
    for file in files:
        validate_task_attachment_type(file)

    user = request.auth["user"]

    with transaction.atomic():
        task = commands.create_task(user=user, project_id=id, **payload.dict())
        for file in files:
            commands.create_task_attachment(file, task)

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
    files: File[List[UploadedFile]] = None,
):
    for file in files:
        validate_task_attachment_type(file)

    user = request.auth["user"]

    with transaction.atomic():
        task = commands.update_task(user=user, task_id=task_id, **payload.dict())
        for file in files:
            commands.create_task_attachment(file, task)

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_task", args=[task.id])
    )

    return task


@router.delete("/tasks/{task_id}", response={204: None})
def delete_task(request: HttpRequest, response: HttpResponse, task_id: int):
    user = request.auth["user"]
    commands.delete_task(user=user, task_id=task_id)

    return 204, None


@router.get("/", response=list[ProjectOutput])
def get_projects(request: HttpRequest, filters: ProjectFilterSchema = Query(...)):
    user = request.auth["user"]

    projects = (
        filters.filter(queries.get_user_projects(user=user))
        if request.GET
        else queries.get_user_projects(user=user)
    )

    return list(projects)


@router.post("/", response={201: ProjectOutput})
def create_project(request: HttpRequest, response: HttpResponse, payload: ProjectInput):
    user = request.auth["user"]
    project = commands.create_project(user=user, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return 201, project


@router.get("/{id}", url_name="get_project", response=ProjectOutput)
def get_project(request: HttpRequest, id: int):
    user = request.auth["user"]
    return queries.get_project(user=user, project_id=id)


@router.patch("/{id}", response=ProjectOutput)
def update_project(
    request: HttpRequest, response: HttpResponse, id: int, payload: ProjectInput
):
    user = request.auth["user"]
    project = commands.update_project(user=user, project_id=id, **payload.dict())

    response["Location"] = request.build_absolute_uri(
        reverse("api-1:get_project", args=[project.id])
    )

    return project


@router.delete("/{id}", response={204: None})
def delete_project(request: HttpRequest, response: HttpResponse, id: int):
    user = request.auth["user"]
    commands.delete_project(user=user, project_id=id)

    return 204, None
