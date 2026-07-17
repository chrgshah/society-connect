"""Django application configuration for cross-cutting core services."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Register the core application and its startup hooks."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        """Load signal receivers after Django initializes installed apps."""
        import core.signals.model_signals  # noqa: F401
