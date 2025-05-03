from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema
from ninja.errors import HttpError
import jwt

from .models import User
from .auth_token import AuthToken
from .queries import get_user_by_id
from .commands import activate_user_account, create_user
from .exceptions import InvalidOrExpiredToken

router = Router()


class UserInput(Schema):
    email: str
    password: str


class AuthResponse(Schema):
    access_token: str
    email: str


class RefreshResponse(Schema):
    access_token: str


@router.post("/register", auth=None)
def register(request: HttpRequest, payload: UserInput):
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already in use.")

    try:
        user = create_user(email=payload.email, password=payload.password)
    except Exception:
        raise HttpError(400, "User creation failed.")

    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse("api-1:activate", args=[user.pk, token])
    )

    send_mail(
        "Activate your account",
        f"Click the link to activate your account: {activation_link}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    return {"success": "User registered successfully!"}


@router.get("/activate/{uid}/{token}", url_name="activate", auth=None)
def activate_account(request: HttpRequest, uid: int, token: str):
    user = get_user_by_id(uid=uid)
    if user.is_active:
        return {"message": "Account is already active."}

    try:
        activate_user_account(user=user, token=token)
    except InvalidOrExpiredToken:
        raise HttpError(401, "Invalid or expired token.")

    return {"message": "Account activated successfully!"}


@router.post("/login", response=AuthResponse, auth=None)
def login_view(request: HttpRequest, response: HttpResponse, payload: UserInput):
    user = authenticate(request, email=payload.email, password=payload.password)
    if not user:
        raise HttpError(401, "Invalid credentials.")
    if not user.is_active:
        raise HttpError(401, "Account is not active.")

    tokens = AuthToken.create_tokens(user.id)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {
        "access_token": tokens["access_token"],
        "email": user.email,
    }


@router.post("/refresh_token", auth=None)
def refresh_token(request: HttpRequest, response: HttpResponse):
    refresh_token = request.COOKIES["refresh_token"]
    try:
        payload = AuthToken.decode_jwt(refresh_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HttpError(401, "Invalid or expired token.")

    user = get_user_by_id(uid=payload["uid"])
    tokens = AuthToken.create_tokens(user.id)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {
        "access_token": tokens["access_token"],
    }


@router.get("/profile")
def user_profile(request: HttpRequest):
    payload = request.auth
    user = get_user_by_id(uid=payload["uid"])
    return {"email": user.email}
