from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import status

from services.models.user import User

from .jwt_service import decode_token, validate_session


class JWTSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if (
            path.startswith("/admin/")
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
            return JsonResponse(
                {"success": False, "message": "Invalid or expired JWT.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = payload.get("user_id")
        jti = payload.get("jti")
        if user_id is None or jti is None:
            return JsonResponse(
                {"success": False, "message": "Invalid token payload.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        session = validate_session(user_id, jti)
        if session is None:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Redis session missing or invalid.",
                    "errors": {},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(id=user_id, is_active=True, deleted_at__isnull=True)
        except User.DoesNotExist:
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
                return JsonResponse(
                    {
                        "success": False,
                        "message": "CSRF validation failed.",
                        "errors": {},
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return self.get_response(request)
