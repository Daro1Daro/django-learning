from datetime import datetime, timedelta
import jwt
from django.conf import settings
from typing import TypedDict


class Tokens(TypedDict):
    access_token: str
    refresh_token: str


class AuthToken:
    @staticmethod
    def encode_jwt(email: str, exp: int) -> str:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(seconds=exp),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def create_tokens(cls, email: str) -> Tokens:
        access_token = cls.encode_jwt(email, settings.JWT_EXP_TIME)
        refresh_token = cls.encode_jwt(email, settings.JWT_REFRESH_EXP_TIME)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
