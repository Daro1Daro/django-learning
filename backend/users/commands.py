from django.contrib.auth.tokens import default_token_generator
from ninja.errors import HttpError

from .models import User
from .exceptions import InvalidActivationToken


def command_activate_user_account(user: User, token: str):
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
    else:
        raise InvalidActivationToken


def command_create_user(email: str, password: str) -> User:
    if User.objects.filter(email=email).exists():
        raise HttpError(400, "Email already in use.")

    return User.objects.create_user(email=email, password=password)
