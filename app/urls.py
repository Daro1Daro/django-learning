from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja.security import HttpBearer
import jwt

from users.api import router as users_router
from users.auth_token import AuthToken


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            return AuthToken.decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


api = NinjaAPI(version="1", auth=AuthBearer)

api.add_router("/auth/", users_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
]
