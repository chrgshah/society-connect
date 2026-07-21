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


@pytest.mark.django_db
def test_put_member_uses_update_behavior(authenticated_client):
    """Verify PUT delegates to the supported member update behavior."""
    member = create_member()
    response = authenticated_client.put(
        f"/api/v1/members/{member.uuid}/", {"last_name": "Updated"}, format="json"
    )
    assert response.status_code == 200
    assert response.json()["data"]["last_name"] == "Updated"


@pytest.mark.django_db
def test_member_options_are_unpaginated_and_only_active(authenticated_client):
    """Verify remote member dropdowns receive a plain active-member array."""
    active = create_member(first_name="Dropdown", is_active=True)
    create_member(
        email="inactive@example.com", membership_number="MEM-INACTIVE", is_active=False
    )

    response = authenticated_client.get("/api/v1/members/options/?search=Dropdown")

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["data"][0]["uuid"] == str(active.uuid)


@pytest.mark.django_db
def test_member_with_active_lending_cannot_be_deactivated(authenticated_client):
    """Protect lending history while a member still holds a book."""
    from tests.helpers import create_book

    member = create_member()
    book = create_book()
    authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )

    response = authenticated_client.delete(f"/api/v1/members/{member.uuid}/")

    assert response.status_code == 409
    assert "active lendings" in response.json()["message"]
