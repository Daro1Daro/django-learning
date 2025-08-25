from .models import User


def get_user_by_id(uid: int) -> User:
    return User.read_model.get_by_id(id=uid)
