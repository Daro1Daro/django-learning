from ninja import NinjaAPI
from ninja.security import HttpBearer
import jwt

from users.auth_token import AuthToken


class InvalidToken(Exception):
    pass


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            return AuthToken.decode_jwt(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidToken


api = NinjaAPI(version="1", auth=AuthBearer())


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {"detail": "Invalid token supplied"}, status=401
    )
