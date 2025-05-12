from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "id")
    search_fields = ("name", "owner__username", "members__username")
    list_filter = ("created_at",)
    filter_horizontal = ("members",)
