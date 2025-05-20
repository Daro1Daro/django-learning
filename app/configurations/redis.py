from os import getenv


class RedisConfig:
    REDIS_URL = f"redis://{getenv('REDIS_USER', 'default')}:{getenv('REDIS_PASSWORD', 'redis_password')}@{getenv('REDIS_HOST', '127.0.0.1')}:{getenv('REDIS_PORT', '6379')}"

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
