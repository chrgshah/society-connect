"""Shared pytest fixtures for API authentication and users."""

import pytest
from rest_framework.test import APIClient

from services.models.user import User


@pytest.fixture(autouse=True)
def disable_redis(monkeypatch):
    """Keep tests isolated from Redis by using the in-memory session fallback."""
    monkeypatch.setattr("core.authentication.redis_session._get_client", lambda: None)


@pytest.fixture
def api_client():
    """Provide an unauthenticated REST framework test client."""
    return APIClient()


@pytest.fixture
def staff_user(db):
    """Create the active user used by authenticated API tests."""
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        # This deterministic credential exists only inside the isolated test database.
        password="Admin@12345",  # nosec B106
    )
    return user


@pytest.fixture
def authenticated_client(api_client, staff_user):
    """Log in the shared user and return a cookie-authenticated client."""
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "Admin@12345"},
        format="json",
    )
    assert response.status_code == 200
    csrf_token = api_client.cookies["csrftoken"].value
    api_client.credentials(HTTP_X_CSRFTOKEN=csrf_token)
    return api_client
