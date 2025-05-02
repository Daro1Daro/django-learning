from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from ninja import NinjaAPI
from ninja.security import HttpBearer

from .models import User
from .schemas import UserInput, AuthResponse, RefreshInput, RefreshResponse
from .utils import decode_jwt, create_tokens


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        payload = decode_jwt(token)
        return payload


api = NinjaAPI(version="1")


@api.post("/register")
def register(request, payload: UserInput):
    if User.objects.filter(email=payload.email).exists():
        return {"error": "Email already in use"}

    try:
        user = User.objects.create_user(email=payload.email, password=payload.password)

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

        return {"success": "User registered successfully"}
    except Exception as e:
        return {"error": str(e)}


@api.post("/login", response=AuthResponse)
def login_view(request, payload: UserInput):
    user = authenticate(request, email=payload.email, password=payload.password)
    if not user:
        return {"error": "Invalid credentials"}
    if not user.is_active:
        return {"error": "Account is not active"}

    tokens = create_tokens(user.email)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "email": user.email,
    }


@api.post("/refresh_token", response=RefreshResponse)
def refresh_token(request, data: RefreshInput):
    payload = decode_jwt(data.refresh_token)
    if not payload:
        return {"error": "Invalid or expired token"}

    user = User.objects.get(email=payload["email"])
    return create_tokens(user.email)


@api.get("/profile", auth=AuthBearer())
def user_profile(request):
    payload = request.auth
    user = User.objects.get(email=payload["email"])
    return {"email": user.email}


@api.get("/activate/{uid}/{token}", url_name="activate")
def activate_account(request, uid: int, token: str):
    user = get_object_or_404(User, pk=uid)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return {"message": "Account activated successfully!"}
    else:
        return {"error": "Invalid or expired token"}
