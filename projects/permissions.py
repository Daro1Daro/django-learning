from enum import StrEnum


class Permissions(StrEnum):
    DELETE_PROJECT = "delete_project"
    UPDATE_PROJECT = "change_project"
    VIEW_PROJECT = "view_project"
    CREATE_TASK = "create_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    VIEW_TASK = "view_task"
