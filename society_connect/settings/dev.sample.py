"""Local development settings template copied to ``dev.py`` by developers."""

import os

DEBUG = True
ALLOWED_HOSTS = ["*"]
CSRF_COOKIE_SECURE = False
JWT_COOKIE_SECURE = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "library_db"),
        "USER": os.environ.get("POSTGRES_USER", "library_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "library_pass"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
