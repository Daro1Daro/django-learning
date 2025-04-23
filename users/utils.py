from datetime import datetime, timedelta
import jwt
from django.conf import settings


def encode_jwt(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_TIME),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str):
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
