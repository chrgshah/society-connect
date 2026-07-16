from .base import *  # noqa: F403, F401

DEBUG = False
CSRF_COOKIE_SECURE = False
JWT_COOKIE_SECURE = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
