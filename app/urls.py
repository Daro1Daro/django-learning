from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja.security import HttpBearer

from users.api import router as users_router
from users.auth_token import AuthToken


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = AuthToken.decode_jwt(token)
        return payload


api = NinjaAPI(version="1", auth=AuthBearer)

api.add_router("/auth/", users_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
