"""Tests for developer OpenAPI and Swagger documentation."""


def test_swagger_ui_is_available_before_login(api_client):
    """Allow developers to open Swagger before authenticating."""
    response = api_client.get("/api/docs/")

    assert response.status_code == 200
    assert b"swagger-ui" in response.content


def test_openapi_schema_is_available_before_login(api_client):
    """Expose login and protected operations in the public developer schema."""
    response = api_client.get("/api/schema/", HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/auth/login/" in schema["paths"]
    assert "/api/v1/categories/" in schema["paths"]
    assert "Before using the API" in schema["info"]["description"]
    assert "enter your `username` and `password`" in schema["info"]["description"]
