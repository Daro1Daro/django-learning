from ninja import NinjaAPI
from ninja.security import HttpBearer
import jwt

from users.auth_token import AuthToken
from users.exceptions import InvalidToken


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = AuthToken.decode_jwt(token)

        if AuthToken.is_token_blacklisted(token):
            raise InvalidToken

        return {"payload": payload, "access_token": token}


api = NinjaAPI(version="1", auth=AuthBearer())


@api.exception_handler(InvalidToken)
@api.exception_handler(jwt.ExpiredSignatureError)
@api.exception_handler(jwt.InvalidTokenError)
def on_invalid_token(request, exc):
    return api.create_response(
        request, {"detail": "Invalid token supplied"}, status=401
    )
