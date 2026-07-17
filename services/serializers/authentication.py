"""Request serializers for login, refresh, and logout operations."""

from rest_framework import serializers

from services.models.user import User


class LoginSerializer(serializers.Serializer):
    """Validate user credentials and expose the matching active user."""

    username = serializers.CharField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the submitted username and password."""
        try:
            user = User.objects.get(
                username=attrs["username"],
                is_active=True,
                deleted_at__isnull=True,
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


class RefreshSerializer(serializers.Serializer):
    """Accept an optional refresh token when a cookie is unavailable."""

    refresh = serializers.CharField(required=False, allow_blank=True)


class LogoutSerializer(serializers.Serializer):
    """Represent the currently body-less logout request."""

    refresh = serializers.CharField(required=False, allow_blank=True)
