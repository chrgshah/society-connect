"""HTTP controllers for cookie-based authentication workflows."""

import jwt
from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.authentication.cookies import clear_auth_cookies, set_auth_cookies
from core.authentication.jwt_service import decode_token, invalidate_session
from core.responses.mixins import ResponseMixin
from services.factories.authentication import AuthenticationFactory
from services.models.user import User
from services.serializers.authentication import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
)
from services.shared.logger import logger


class AuthCsrfController(ResponseMixin, APIView):
    """Issue the CSRF cookie required by state-changing requests."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """Create a CSRF token for an unauthenticated client."""
        get_token(request)
        return self.success_response(message="CSRF cookie created.")


class AuthLoginController(ResponseMixin, APIView):
    """Validate credentials and establish an authenticated session."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Log in a user and return authentication cookies."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthenticationFactory.login_user(serializer.validated_data["user"])
        get_token(request)
        response = self.success_response(
            message="Logged in successfully.", status_code=status.HTTP_200_OK
        )
        logger.info(
            "[SOCIETY_CONNECT] event=login_succeeded user_id=%s",
            serializer.validated_data["user"].id,
        )
        return set_auth_cookies(response, tokens)


class AuthRefreshController(ResponseMixin, APIView):
    """Replace an eligible refresh token with a fresh token pair."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Refresh authentication cookies using the submitted cookie/token."""
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh") or request.COOKIES.get(
            settings.JWT_REFRESH_COOKIE_NAME
        )
        if not refresh_token:
            logger.warning(
                "[SOCIETY_CONNECT] event=token_refresh_rejected reason=missing_token"
            )
            return self.error_response(
                message="Refresh cookie was not provided.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            tokens = AuthenticationFactory.refresh_token(refresh_token)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            logger.warning(
                "[SOCIETY_CONNECT] event=token_refresh_rejected "
                "reason=invalid_or_expired_token"
            )
            response = self.error_response(
                message="Refresh token is invalid or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            return clear_auth_cookies(response)
        logger.info("[SOCIETY_CONNECT] event=token_refresh_succeeded")
        response = self.success_response(
            message="Token refreshed successfully.", status_code=status.HTTP_200_OK
        )
        return set_auth_cookies(response, tokens)


class AuthLogoutController(ResponseMixin, APIView):
    """Invalidate the current session and clear authentication cookies."""

    def post(self, request):
        """Log out the authenticated user from the current session."""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if getattr(request, "session_info", None):
            invalidate_session(request.user.id, request.session_info["jti"])
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if refresh_token:
            try:
                refresh_payload = decode_token(refresh_token)
                invalidate_session(request.user.id, refresh_payload["jti"])
            except (jwt.InvalidTokenError, KeyError):
                logger.warning(
                    "[SOCIETY_CONNECT] event=logout_refresh_cleanup_skipped "
                    "reason=invalid_token user_id=%s",
                    request.user.id,
                )
        logger.info(
            "[SOCIETY_CONNECT] event=logout_succeeded user_id=%s", request.user.id
        )
        response = self.success_response(
            message="Logged out successfully.", status_code=status.HTTP_200_OK
        )
        return clear_auth_cookies(response)


class AuthMeController(ResponseMixin, APIView):
    """Expose the current authenticated user's basic profile."""

    def get(self, request):
        """Return identity fields for the request user."""
        return self.success_response(
            data={
                "id": request.user.id,
                "uuid": request.user.uuid,
                "email": request.user.email,
                "username": request.user.username,
            },
            message="User profile retrieved.",
        )
