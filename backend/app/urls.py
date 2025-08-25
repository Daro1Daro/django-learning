from django.contrib import admin
from django.urls import path

from users.api import router as users_router
from projects.api import router as projects_router
from .api import api

api.add_router("/auth/", users_router)
api.add_router("/projects/", projects_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
