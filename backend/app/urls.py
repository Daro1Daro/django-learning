from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from users.api import router as users_router
from projects.api import router as projects_router
from .api import api

api.add_router("/auth/", users_router)
api.add_router("/projects/", projects_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
