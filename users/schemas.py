from ninja import Schema


class UserInput(Schema):
    email: str
    password: str


class AuthResponse(Schema):
    access_token: str
    refresh_token: str
    email: str


class RefreshInput(Schema):
    refresh_token: str


class RefreshResponse(Schema):
    access_token: str
    refresh_token: str
