"""Create, decode, refresh, and invalidate JWT-backed user sessions."""

from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from services.models.user import User
from services.shared.logger import logger

from .redis_session import create_redis_session, delete_redis_session, get_redis_session


def create_tokens(user):
    """Create a token pair and persist both server-side sessions."""
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    access_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.JWT_ACCESS_TOKEN_LIFETIME
    )
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.JWT_REFRESH_TOKEN_LIFETIME
    )
    create_redis_session(user.id, user.username, access_token["jti"], access_expires_at)
    create_redis_session(
        user.id, user.username, refresh_token["jti"], refresh_expires_at
    )
    logger.info("[SOCIETY_CONNECT] event=auth_tokens_created user_id=%s", user.id)
    return {"access": str(access_token), "refresh": str(refresh_token)}


def decode_token(token: str):
    """Decode a token while validating its signature and expiry."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_exp": True},
    )


def validate_session(user_id: int, jti: str):
    """Return an active, unexpired session or ``None`` when invalid."""
    session = get_redis_session(user_id, jti)
    if session is None:
        logger.warning(
            "[SOCIETY_CONNECT] event=auth_session_not_found user_id=%s", user_id
        )
        return None
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_redis_session(user_id, jti)
        logger.warning(
            "[SOCIETY_CONNECT] event=auth_session_expired user_id=%s", user_id
        )
        return None
    if not session.get("is_active", False):
        logger.warning(
            "[SOCIETY_CONNECT] event=auth_session_inactive user_id=%s", user_id
        )
        return None
    return session


def refresh_tokens(refresh_token: str):
    """Require a live refresh session, rotate it, and issue a new token pair."""
    payload = jwt.decode(
        refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_exp": True},
    )
    user_id = payload["user_id"]
    refresh_jti = payload["jti"]
    if validate_session(user_id, refresh_jti) is None:
        raise jwt.InvalidTokenError("Refresh session missing or invalid.")
    user = User.objects.get(id=user_id, is_active=True)
    delete_redis_session(user_id, refresh_jti)
    return create_tokens(user)


def invalidate_session(user_id: int, jti: str):
    """Remove an access session so the associated token is no longer valid."""
    delete_redis_session(user_id, jti)
    logger.info("[SOCIETY_CONNECT] event=auth_session_invalidated user_id=%s", user_id)
