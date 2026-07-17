"""Integration tests for member creation and listing APIs."""

import pytest

from tests.helpers import create_member


@pytest.mark.django_db
def test_create_member(authenticated_client):
    """Verify a valid member can be registered."""
    response = authenticated_client.post(
        "/api/v1/members/",
        {
            "first_name": "Chirag",
            "last_name": "Shah",
            "email": "chirag@example.com",
            "phone": "+1234567890",
            "address": "123 Oak",
            "membership_number": "MEM-000010",
            "membership_date": "2024-01-01",
            "is_active": True,
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_list_members(authenticated_client):
    """Verify the member endpoint returns existing members."""
    create_member(email="member@example.com", membership_number="MEM-111111")
    response = authenticated_client.get("/api/v1/members/")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_get_update_and_soft_delete_member(authenticated_client):
    """Verify the member detail lifecycle and soft-deletion behavior."""
    member = create_member()

    detail = authenticated_client.get(f"/api/v1/members/{member.uuid}/")
    updated = authenticated_client.patch(
        f"/api/v1/members/{member.uuid}/",
        {"first_name": "Janet"},
        format="json",
    )
    deleted = authenticated_client.delete(f"/api/v1/members/{member.uuid}/")
    missing = authenticated_client.get(f"/api/v1/members/{member.uuid}/")

    assert detail.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["data"]["first_name"] == "Janet"
    assert deleted.status_code == 200
    assert missing.status_code == 404


@pytest.mark.django_db
def test_create_member_rejects_duplicate_email(authenticated_client):
    """Verify two active members cannot share an email address."""
    create_member(email="duplicate@example.com")
    response = authenticated_client.post(
        "/api/v1/members/",
        {
            "first_name": "Other",
            "last_name": "Member",
            "email": "duplicate@example.com",
            "phone": "+1234567890",
            "membership_number": "MEM-999999",
            "membership_date": "2024-01-01",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.json()["errors"]
