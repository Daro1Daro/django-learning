from django.contrib import admin
from django.urls import path

from users.api import router as users_router
from .api import api

api.add_router("/auth/", users_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
