"""Facade for authentication token and session operations."""

from core.authentication.jwt_service import create_tokens, invalidate_session


class AuthenticationFactory:
    """Coordinate token creation, refresh, and logout workflows."""

    @staticmethod
    def login_user(user):
        """Create authentication tokens for a validated user."""
        return create_tokens(user)

    @staticmethod
    def refresh_token(refresh_token):
        """Exchange a valid refresh token for a new token pair."""
        from core.authentication.jwt_service import refresh_tokens

        return refresh_tokens(refresh_token)

    @staticmethod
    def logout_user(user_id: int, jti: str):
        """Invalidate a user's identified access session."""
        invalidate_session(user_id, jti)
