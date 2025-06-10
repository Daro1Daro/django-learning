from enum import StrEnum


class Permissions(StrEnum):
    DELETE = "delete"
    UPDATE = "change"
    VIEW = "view"
    CREATE_project = "create_project"
    CREATE_TASK = "create_task"
