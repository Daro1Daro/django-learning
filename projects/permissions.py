from enum import StrEnum


class Permissions(StrEnum):
    DELETE_PROJECT = "delete_project"
    UPDATE_PROJECT = "change_project"
    VIEW_PROJECT = "view_project"
