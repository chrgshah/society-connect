"""Request serializers for login, refresh, and logout operations."""

from rest_framework import serializers

from services.models.user import User


class EmptySerializer(serializers.Serializer):
    """Describe an endpoint that has no request fields."""

    pass


class CurrentUserSerializer(serializers.Serializer):
    """Describe the identity returned for the authenticated user."""

    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)


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
