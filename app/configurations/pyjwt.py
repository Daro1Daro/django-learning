from os import getenv


class PyJWTConfig:
    JWT_SECRET = getenv("DJANGO_SECRET_KEY", "JWT_secret")
    JWT_ALGORITHM = "HS256"
    JWT_EXP_TIME = 30 * 60
    JWT_REFRESH_EXP_TIME = 7 * 24 * 60 * 60
