from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja.security import HttpBearer
import jwt

from users.models import User
from users.auth_token import AuthToken
from users.exceptions import InvalidToken
from projects.exceptions import ProjectPermissionDenied


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = AuthToken.decode_jwt(token)

        if AuthToken.is_token_blacklisted(token):
            raise InvalidToken

        user: User = get_object_or_404(User, id=payload["uid"])

        return {"payload": payload, "access_token": token, "user": user}


api = NinjaAPI(version="1", auth=AuthBearer())


@api.exception_handler(InvalidToken)
@api.exception_handler(jwt.ExpiredSignatureError)
@api.exception_handler(jwt.InvalidTokenError)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {"detail": "Invalid token supplied"}, status=401
    )


@api.exception_handler(ProjectPermissionDenied)
def on_project_permission_denied(request, exc):
    return api.create_response(request, {"detail": "Access denied"}, status=403)
