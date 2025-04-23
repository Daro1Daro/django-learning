from ninja import Schema


class UserInput(Schema):
    email: str
    password: str


class AuthResponse(Schema):
    token: str
    email: str
