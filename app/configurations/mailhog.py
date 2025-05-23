from os import getenv


class MailHogConfig:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = getenv("EMAIL_HOST", "127.0.0.1")
    EMAIL_PORT = getenv("EMAIL_PORT", "1025")
    DEFAULT_FROM_EMAIL = "noreply@test.com"
    PASSWORD_RESET_TIMEOUT = 6 * 60 * 60
