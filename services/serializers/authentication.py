from rest_framework import serializers

from services.models.user import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(trim_whitespace=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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
    refresh = serializers.CharField(required=False, allow_blank=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True)
