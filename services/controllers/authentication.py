from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.authentication.jwt_service import invalidate_session
from core.responses.mixins import ResponseMixin
from services.factories.authentication import AuthenticationFactory
from services.serializers.authentication import LoginSerializer, LogoutSerializer, RefreshSerializer


def set_auth_cookies(response, tokens):
    response.set_cookie(
        settings.JWT_ACCESS_COOKIE_NAME,
        tokens["access"],
        max_age=settings.JWT_ACCESS_TOKEN_LIFETIME,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        tokens["refresh"],
        max_age=settings.JWT_REFRESH_TOKEN_LIFETIME,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/api/v1/auth/",
    )
    return response


class AuthCsrfController(ResponseMixin, APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)
        return self.success_response(message="CSRF cookie created.")


class AuthLoginController(ResponseMixin, APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthenticationFactory.login_user(serializer.validated_data["user"])
        get_token(request)
        response = self.success_response(message="Logged in successfully.", status_code=status.HTTP_200_OK)
        return set_auth_cookies(response, tokens)


class AuthRefreshController(ResponseMixin, APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh") or request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return self.error_response(message="Refresh cookie was not provided.", status_code=status.HTTP_401_UNAUTHORIZED)
        tokens = AuthenticationFactory.refresh_token(refresh_token)
        response = self.success_response(message="Token refreshed successfully.", status_code=status.HTTP_200_OK)
        return set_auth_cookies(response, tokens)


class AuthLogoutController(ResponseMixin, APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if getattr(request, "session_info", None):
            invalidate_session(request.user.id, request.session_info["jti"])
        response = self.success_response(message="Logged out successfully.", status_code=status.HTTP_200_OK)
        response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME, path="/", samesite=settings.JWT_COOKIE_SAMESITE)
        response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME, path="/api/v1/auth/", samesite=settings.JWT_COOKIE_SAMESITE)
        return response


class AuthMeController(ResponseMixin, APIView):
    def get(self, request):
        return self.success_response(
            data={
                "id": request.user.id,
                "uuid": request.user.uuid,
                "email": request.user.email,
                "username": request.user.username,
            },
            message="User profile retrieved.",
        )
