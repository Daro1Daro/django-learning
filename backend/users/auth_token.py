from datetime import datetime, timedelta
from typing import TypedDict
from django.conf import settings
from django.core.cache import cache
import jwt


class Tokens(TypedDict):
    access_token: str
    refresh_token: str


class AuthToken:
    @staticmethod
    def encode_jwt(uid: int, exp: int) -> str:
        payload = {
            "uid": uid,
            "exp": datetime.utcnow() + timedelta(seconds=exp),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_jwt(token: str) -> dict:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

    @classmethod
    def create_tokens(cls, uid: int) -> Tokens:
        access_token = cls.encode_jwt(uid, settings.JWT_EXP_TIME)
        refresh_token = cls.encode_jwt(uid, settings.JWT_REFRESH_EXP_TIME)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def blacklist_token(token: str, timeout: int):
        cache.set(token, "blacklisted", timeout=timeout)

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        return cache.get(token) == "blacklisted"
