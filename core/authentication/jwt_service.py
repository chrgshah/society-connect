from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from services.models.user import User

from .redis_session import create_redis_session, delete_redis_session, get_redis_session

def create_tokens(user):
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
    jti = access_token["jti"]
    create_redis_session(user.id, user.username, jti, expires_at)
    return {"access": str(access_token), "refresh": str(refresh_token)}


def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": True})


def validate_session(user_id: int, jti: str):
    session = get_redis_session(user_id, jti)
    if session is None:
        return None
    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_redis_session(user_id, jti)
        return None
    if not session.get("is_active", False):
        return None
    return session


def refresh_tokens(refresh_token: str):
    payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": True})
    user = User.objects.get(id=payload["user_id"], is_active=True, deleted_at__isnull=True)
    return create_tokens(user)


def invalidate_session(user_id: int, jti: str):
    delete_redis_session(user_id, jti)
