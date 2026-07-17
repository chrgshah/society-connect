"""Integration tests for login, logout, and protected authentication APIs."""

import pytest

from services.shared.password import hash_string


@pytest.mark.django_db
def test_successful_login(api_client, staff_user):
    """Verify valid credentials establish cookie authentication."""
    response = api_client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "Admin@12345"},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.cookies["nls_access"]["httponly"] is True
    assert response.cookies["nls_refresh"]["httponly"] is True
    assert "access" not in response.json()["data"]
    assert "refresh" not in response.json()["data"]
    staff_user.refresh_from_db()
    assert staff_user.password == hash_string("Admin@12345")
    assert len(staff_user.password) == 64


@pytest.mark.django_db
def test_invalid_login(api_client, staff_user):
    """Verify invalid credentials are rejected."""
    response = api_client.post(
        "/api/v1/auth/login/", {"username": "admin", "password": "wrong"}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_protected_api_without_token(api_client):
    """Verify protected endpoints reject requests without an access token."""
    response = api_client.get("/api/v1/members/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_profile_and_logout(api_client, staff_user):
    """Verify an authenticated user can read their profile and log out."""
    api_client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "Admin@12345"},
        format="json",
    )
    csrf_token = api_client.cookies["csrftoken"].value
    api_client.credentials(HTTP_X_CSRFTOKEN=csrf_token)

    profile_response = api_client.get("/api/v1/auth/me/")
    assert profile_response.status_code == 200
    assert profile_response.json()["data"]["email"] == "admin@example.com"

    logout_response = api_client.post("/api/v1/auth/logout/", {}, format="json")
    assert logout_response.status_code == 200
    assert api_client.get("/api/v1/auth/me/").status_code == 401


@pytest.mark.django_db
def test_csrf_endpoint_sets_cookie(api_client):
    """Verify clients can initialize CSRF protection before logging in."""
    response = api_client.get("/api/v1/auth/csrf/")

    assert response.status_code == 200
    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_refresh_requires_token(api_client):
    """Verify refresh requests without a token are rejected."""
    response = api_client.post("/api/v1/auth/refresh/", {}, format="json")

    assert response.status_code == 401
    assert response.json()["success"] is False


@pytest.mark.django_db
def test_refresh_uses_login_cookie(api_client, staff_user):
    """Verify a login refresh cookie can issue a new token pair."""
    login = api_client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "Admin@12345"},
        format="json",
    )
    assert login.status_code == 200

    response = api_client.post("/api/v1/auth/refresh/", {}, format="json")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "nls_access" in response.cookies


@pytest.mark.django_db
def test_refresh_rejects_invalid_token_and_clears_cookies(api_client):
    """Verify stale refresh cookies return 401 and are removed."""
    api_client.cookies["nls_refresh"] = "invalid-token"

    response = api_client.post("/api/v1/auth/refresh/", {}, format="json")

    assert response.status_code == 401
    assert response.json()["message"] == "Refresh token is invalid or expired."
    assert response.cookies["nls_access"]["max-age"] == 0
    assert response.cookies["nls_refresh"]["max-age"] == 0
