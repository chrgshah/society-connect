"""Authenticate API requests using JWT cookies and server-side sessions."""

from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import status

from services.models.user import User
from services.shared.logger import logger

from .cookies import clear_auth_cookies
from .jwt_service import decode_token, validate_session


class JWTSessionMiddleware:
    """Attach authenticated users to requests and enforce CSRF protection."""

    def __init__(self, get_response):
        """Store the next callable in Django's middleware chain."""
        self.get_response = get_response

    def __call__(self, request):
        """Authenticate a request, validate CSRF when needed, and continue."""
        path = request.path
        if (
            path.startswith("/admin/")
            or path.startswith("/api/docs/")
            or path.startswith("/api/schema/")
            or path.startswith("/static/")
            or path.startswith("/media/")
            or path
            in {
                "/api/v1/auth/login/",
                "/api/v1/auth/refresh/",
                "/api/v1/auth/csrf/",
                "/api/v1/health/",
            }
        ):
            return self.get_response(request)

        token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)
        if not token:
            logger.warning(
                "[SOCIETY_CONNECT] event=auth_rejected reason=missing_token "
                "method=%s path=%s",
                request.method,
                path,
            )
            return JsonResponse(
                {
                    "success": False,
                    "message": "Authentication credentials were not provided.",
                    "errors": {},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            payload = decode_token(token)
        except Exception:
            logger.exception(
                "[SOCIETY_CONNECT] event=auth_rejected reason=invalid_token "
                "method=%s path=%s",
                request.method,
                path,
            )
            return JsonResponse(
                {"success": False, "message": "Invalid or expired JWT.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = payload.get("user_id")
        jti = payload.get("jti")
        if user_id is None or jti is None:
            logger.warning(
                "[SOCIETY_CONNECT] event=auth_rejected reason=invalid_payload "
                "method=%s path=%s",
                request.method,
                path,
            )
            return JsonResponse(
                {"success": False, "message": "Invalid token payload.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        session = validate_session(user_id, jti)
        if session is None:
            logger.warning(
                "[SOCIETY_CONNECT] event=auth_rejected reason=invalid_session "
                "user_id=%s method=%s path=%s",
                user_id,
                request.method,
                path,
            )
            response = JsonResponse(
                {
                    "success": False,
                    "message": "Redis session missing or invalid.",
                    "errors": {},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
            return clear_auth_cookies(response)

        try:
            user = User.objects.get(id=user_id, is_active=True, deleted_at__isnull=True)
        except User.DoesNotExist:
            logger.warning(
                "[SOCIETY_CONNECT] event=auth_rejected reason=user_not_found "
                "user_id=%s method=%s path=%s",
                user_id,
                request.method,
                path,
            )
            return JsonResponse(
                {"success": False, "message": "User not found.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.user = user
        request.session_info = session

        if request.method not in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            csrf_middleware = CsrfViewMiddleware(lambda req: self.get_response(req))
            csrf_failure = csrf_middleware.process_view(
                request, lambda req: None, (), {}
            )
            if csrf_failure is not None:
                logger.warning(
                    "[SOCIETY_CONNECT] event=auth_rejected reason=csrf_failed "
                    "user_id=%s method=%s path=%s",
                    user_id,
                    request.method,
                    path,
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": "CSRF validation failed.",
                        "errors": {},
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return self.get_response(request)
