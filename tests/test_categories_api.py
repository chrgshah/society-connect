"""Integration tests for category catalog APIs."""

import pytest
from django.core.management import call_command

from services.models.category import Category
from tests.helpers import create_category


@pytest.mark.django_db
def test_default_category_fixture_can_be_loaded_repeatedly():
    """Verify Docker restarts can safely reload the default categories."""
    call_command("loaddata", "2_categories", verbosity=0)
    call_command("loaddata", "2_categories", verbosity=0)

    assert Category.objects.count() == 5
    assert set(Category.objects.values_list("name", flat=True)) == {
        "Biography",
        "Fiction",
        "History",
        "Mystery",
        "Science",
    }


@pytest.mark.django_db
def test_list_categories(authenticated_client):
    """Verify the category endpoint returns existing categories."""
    category = create_category(name="Fiction")

    response = authenticated_client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert response.json()["data"]["results"][0]["uuid"] == str(category.uuid)
    assert response.json()["data"]["results"][0]["name"] == "Fiction"


@pytest.mark.django_db
def test_category_crud(authenticated_client):
    """Verify categories can be created, retrieved, updated, and soft-deleted."""
    created = authenticated_client.post(
        "/api/v1/categories/",
        {"name": "Technology", "description": "Technology books"},
        format="json",
    )
    assert created.status_code == 201
    category_uuid = created.json()["data"]["uuid"]

    detail = authenticated_client.get(f"/api/v1/categories/{category_uuid}/")
    assert detail.status_code == 200
    assert detail.json()["data"]["name"] == "Technology"

    updated = authenticated_client.patch(
        f"/api/v1/categories/{category_uuid}/",
        {"description": "Updated description"},
        format="json",
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["description"] == "Updated description"

    deleted = authenticated_client.delete(f"/api/v1/categories/{category_uuid}/")
    missing = authenticated_client.get(f"/api/v1/categories/{category_uuid}/")
    assert deleted.status_code == 200
    assert missing.status_code == 404


@pytest.mark.django_db
def test_category_options_are_unpaginated(authenticated_client):
    """Verify category dropdown lookups return a plain searchable array."""
    category = create_category(name="Dropdown Category")

    response = authenticated_client.get("/api/v1/categories/options/?search=Dropdown")

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert response.json()["data"][0]["uuid"] == str(category.uuid)


@pytest.mark.django_db
def test_put_category_uses_update_behavior(authenticated_client):
    """Verify PUT delegates to the category partial-update implementation."""
    category = create_category()

    response = authenticated_client.put(
        f"/api/v1/categories/{category.uuid}/",
        {"description": "Updated through PUT"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["data"]["description"] == "Updated through PUT"


@pytest.mark.django_db
def test_category_rejects_description_over_2500_characters(authenticated_client):
    """Verify category descriptions enforce the documented maximum length."""
    response = authenticated_client.post(
        "/api/v1/categories/",
        {"name": "Too Long", "description": "x" * 2501},
        format="json",
    )

    assert response.status_code == 400
    assert "description" in response.json()["errors"]
