"""Set and clear the browser cookies used by JWT authentication."""

from django.conf import settings


def set_auth_cookies(response, tokens):
    """Attach secure access and refresh cookies to an API response."""
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


def clear_auth_cookies(response):
    """Remove access and refresh cookies from an API response."""
    response.delete_cookie(
        settings.JWT_ACCESS_COOKIE_NAME,
        path="/",
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE_NAME,
        path="/api/v1/auth/",
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    return response
