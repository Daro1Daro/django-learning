from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Project


@admin.register(Project)
class ProjectAdmin(GuardedModelAdmin):
    list_display = ("name", "owner", "created_at", "id")
    search_fields = ("name", "owner__username", "members__username")
    list_filter = ("created_at",)
    filter_horizontal = ("members",)
