from os import getenv


class RedisConfig:
    REDIS_URL = f"redis://{getenv('REDIS_USER')}:{getenv('REDIS_PASSWORD')}@redis:6379"

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
