from os import getenv


class MailHogConfig:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = getenv("EMAIL_HOST")
    EMAIL_PORT = getenv("EMAIL_PORT")
    DEFAULT_FROM_EMAIL = "noreply@test.com"
    PASSWORD_RESET_TIMEOUT = 6 * 60 * 60
