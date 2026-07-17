"""Staging settings template copied to ``stage.py`` during deployment."""

import os

# Staging should behave like production while allowing environment-specific
# hosts, cookies, and database credentials.
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
CSRF_COOKIE_SECURE = (
    os.environ.get("CSRF_COOKIE_SECURE", "true").lower() == "true"
)
JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "true").lower() == "true"

if not os.environ.get("POSTGRES_PASSWORD"):
    raise ValueError("POSTGRES_PASSWORD environment variable is required in staging")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "society_connect_stage"),
        "USER": os.environ.get("POSTGRES_USER", "society_connect_stage"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
