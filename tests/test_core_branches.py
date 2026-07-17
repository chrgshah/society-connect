"""Focused unit tests for authentication, sessions, and error branches."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from django.http import HttpResponse, JsonResponse
from django.test import RequestFactory
from rest_framework.exceptions import NotFound

from core.authentication import jwt_service, middleware, redis_session
from core.exceptions.handlers import exception_handler

ORIGINAL_GET_REDIS_CLIENT = redis_session._get_client


def test_validate_session_rejects_missing_expired_and_inactive(monkeypatch):
    """Verify every invalid server-side session state is rejected."""
    monkeypatch.setattr(jwt_service, "get_redis_session", lambda *_: None)
    assert jwt_service.validate_session(1, "jti") is None

    deleted = Mock()
    monkeypatch.setattr(jwt_service, "delete_redis_session", deleted)
    monkeypatch.setattr(
        jwt_service,
        "get_redis_session",
        lambda *_: {
            "expires_at": (
                datetime.now(timezone.utc) - timedelta(seconds=1)
            ).isoformat(),
            "is_active": True,
        },
    )
    assert jwt_service.validate_session(1, "jti") is None
    deleted.assert_called_once_with(1, "jti")

    monkeypatch.setattr(
        jwt_service,
        "get_redis_session",
        lambda *_: {
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "is_active": False,
        },
    )
    assert jwt_service.validate_session(1, "jti") is None


def test_decode_and_refresh_token_helpers(monkeypatch):
    """Verify JWT helpers delegate decoded identity to token creation."""
    monkeypatch.setattr(
        jwt_service.jwt, "decode", lambda *_args, **_kwargs: {"user_id": 7}
    )
    user = object()
    monkeypatch.setattr(jwt_service.User.objects, "get", lambda **_kwargs: user)
    monkeypatch.setattr(jwt_service, "create_tokens", lambda value: {"user": value})

    assert jwt_service.decode_token("token") == {"user_id": 7}
    assert jwt_service.refresh_tokens("refresh") == {"user": user}


def test_redis_client_creation_failure(monkeypatch):
    """Verify Redis construction failures select the memory fallback."""
    monkeypatch.setattr(
        redis_session.redis.Redis,
        "from_url",
        Mock(side_effect=RuntimeError("unavailable")),
    )
    assert ORIGINAL_GET_REDIS_CLIENT() is None


def test_redis_session_success_paths(monkeypatch):
    """Verify Redis-backed session create, read, and delete operations."""
    client = Mock()
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    monkeypatch.setattr(redis_session, "_get_client", lambda: client)

    payload = redis_session.create_redis_session(1, "user", "jti", expires)
    client.get.return_value = json.dumps(payload)

    assert redis_session.get_redis_session(1, "jti") == payload
    redis_session.delete_redis_session(1, "jti")
    client.setex.assert_called_once()
    client.delete.assert_called_once()


def test_redis_session_failure_paths_use_memory(monkeypatch):
    """Verify Redis operation failures consistently fall back to memory."""
    client = Mock()
    client.setex.side_effect = RuntimeError("write")
    client.get.side_effect = RuntimeError("read")
    client.delete.side_effect = RuntimeError("delete")
    monkeypatch.setattr(redis_session, "_get_client", lambda: client)
    expires = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = redis_session.create_redis_session(2, "user", "jti", expires)
    assert redis_session.get_redis_session(2, "jti") == payload
    redis_session.delete_redis_session(2, "jti")
    assert redis_session.get_redis_session(2, "jti") is None


@pytest.mark.parametrize(
    ("payload", "session", "user", "message"),
    [
        (RuntimeError("bad token"), None, None, "Invalid or expired JWT."),
        ({}, None, None, "Invalid token payload."),
        ({"user_id": 1, "jti": "jti"}, None, None, "Redis session missing or invalid."),
        ({"user_id": 1, "jti": "jti"}, {"active": True}, None, "User not found."),
    ],
)
def test_middleware_authentication_rejections(
    monkeypatch, payload, session, user, message
):
    """Verify middleware returns the correct response for authentication failures."""
    request = RequestFactory().get("/api/v1/members/")
    request.COOKIES["nls_access"] = "token"
    if isinstance(payload, Exception):
        monkeypatch.setattr(middleware, "decode_token", Mock(side_effect=payload))
    else:
        monkeypatch.setattr(middleware, "decode_token", lambda _token: payload)
    monkeypatch.setattr(middleware, "validate_session", lambda *_: session)
    if user is None:
        monkeypatch.setattr(
            middleware.User.objects,
            "get",
            Mock(side_effect=middleware.User.DoesNotExist),
        )

    response = middleware.JWTSessionMiddleware(HttpResponse)(request)

    assert response.status_code == 401
    assert json.loads(response.content)["message"] == message


def test_middleware_rejects_failed_csrf(monkeypatch, staff_user):
    """Verify authenticated unsafe requests still require valid CSRF."""
    request = RequestFactory().post("/api/v1/members/")
    request.COOKIES["nls_access"] = "token"
    monkeypatch.setattr(
        middleware,
        "decode_token",
        lambda _token: {"user_id": staff_user.id, "jti": "jti"},
    )
    monkeypatch.setattr(middleware, "validate_session", lambda *_: {"active": True})
    monkeypatch.setattr(
        middleware.CsrfViewMiddleware,
        "process_view",
        lambda *_args, **_kwargs: JsonResponse({}, status=403),
    )

    response = middleware.JWTSessionMiddleware(HttpResponse)(request)

    assert response.status_code == 403


def test_exception_handler_handles_unmapped_exception():
    """Verify unknown exceptions return no response after being logged."""
    assert exception_handler(RuntimeError("boom"), {}) is None
    response = exception_handler(NotFound("missing"), {})
    assert response.status_code == 404
    assert response.data["message"] == "missing"
