from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from ninja import Router, Schema
from ninja.errors import HttpError

from .auth_token import AuthToken
from .queries import get_user_by_id
from .commands import activate_user_account, create_user
from .exceptions import InvalidActivationToken, InvalidToken

router = Router()


class UserInput(Schema):
    email: str
    password: str


class AuthResponse(Schema):
    access_token: str
    email: str


class RefreshResponse(Schema):
    access_token: str


@router.post("/register", url_name="register", auth=None)
def register(request: HttpRequest, payload: UserInput):
    try:
        user = create_user(email=payload.email, password=payload.password)
    except (TypeError, ValueError):
        raise HttpError(400, "User creation failed.")

    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse("api-1:activate", args=[user.pk, token])
    )

    send_mail(
        subject="Activate your account",
        message=f"Click the link to activate your account: {activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return {"detail": "User registered successfully!"}


@router.get("/activate/{uid}/{token}", url_name="activate", auth=None)
def activate_account(request: HttpRequest, uid: int, token: str):
    user = get_user_by_id(uid=uid)
    if user.is_active:
        return {"detail": "Account is already active."}

    try:
        activate_user_account(user=user, token=token)
    except InvalidActivationToken:
        raise HttpError(401, "Invalid or expired token.")

    return {"detail": "Account activated successfully!"}


@router.post("/login", url_name="login", response=AuthResponse, auth=None)
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
    payload = AuthToken.decode_jwt(refresh_token)

    if AuthToken.is_token_blacklisted(refresh_token):
        raise InvalidToken

    user = get_user_by_id(uid=payload["uid"])
    new_tokens = AuthToken.create_tokens(user.id)

    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    AuthToken.blacklist_token(refresh_token, settings.JWT_REFRESH_EXP_TIME)

    return {
        "access_token": new_tokens["access_token"],
    }


@router.post("/logout", url_name="logout")
def logout(request: HttpRequest):
    access_token = request.auth["access_token"]
    refresh_token = request.COOKIES["refresh_token"]

    # TODO: compute ttl
    AuthToken.blacklist_token(token=access_token, timeout=settings.JWT_EXP_TIME)
    AuthToken.blacklist_token(
        token=refresh_token, timeout=settings.JWT_REFRESH_EXP_TIME
    )

    return {"detail": "You have successfully logged out."}


@router.get("/profile")
def user_profile(request: HttpRequest):
    user = request.auth["user"]
    return {"email": user.email}
