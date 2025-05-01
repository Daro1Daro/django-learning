from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from users.api import router as users_router


api = NinjaAPI(version="1")

api.add_router("/auth/", users_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
