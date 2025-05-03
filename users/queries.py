from django.shortcuts import get_object_or_404

from .models import User


def get_user_by_id(uid: int) -> User:
    user = get_object_or_404(User, id=uid)
    return user
