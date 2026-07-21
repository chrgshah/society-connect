"""Django application configuration for society service features."""

from django.apps import AppConfig


class ServicesConfig(AppConfig):
    """Register the services application with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "services"

    def ready(self):
        """Load OpenAPI extensions when Django initializes the application."""
        from services import schema  # noqa: F401
