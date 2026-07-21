"""OpenAPI extensions for Society Connect's cookie authentication."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTSessionCookieScheme(OpenApiAuthenticationExtension):
    """Describe the HTTP-only access cookie enforced by JWTSessionMiddleware."""

    target_class = "rest_framework.authentication.SessionAuthentication"
    name = "jwtCookieAuth"

    def get_security_definition(self, auto_schema):
        """Return the OpenAPI cookie security definition."""
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "nls_access",
            "description": (
                "Set automatically by POST /api/v1/auth/login/. You do not need "
                "to copy the HTTP-only cookie into Swagger."
            ),
        }
