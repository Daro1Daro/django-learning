from django.contrib.auth.tokens import default_token_generator

from .models import User
from .exceptions import InvalidActivationToken


def activate_user_account(user: User, token: str):
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
    else:
        raise InvalidActivationToken


def create_user(email: str, password: str) -> User:
    return User.objects.create_user(email=email, password=password)
