"""Integration tests for category and book catalog APIs."""

import pytest

from tests.helpers import create_book, create_category


@pytest.mark.django_db
def test_create_book(authenticated_client):
    """Verify a valid book can be added to the catalog."""
    category = create_category(name="Category")
    response = authenticated_client.post(
        "/api/v1/books/",
        {
            "isbn": "9781111111111",
            "title": "Django Basics",
            "author": "Author",
            "category_uuid": str(category.uuid),
            "publisher": "Example",
            "published_year": 2024,
            "description": "A demo",
            "total_copies": 3,
            "available_copies": 3,
            "shelf_location": "B2",
            "is_active": True,
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["author"] == "Author"


@pytest.mark.django_db
def test_update_book_author(authenticated_client):
    """Verify a book's author can be updated."""
    book = create_book(author="Original Author")

    response = authenticated_client.patch(
        f"/api/v1/books/{book.uuid}/",
        {"author": "Updated Author"},
        format="json",
    )

    assert response.status_code == 200
    book.refresh_from_db()
    assert book.author == "Updated Author"
    assert response.json()["data"]["author"] == "Updated Author"


@pytest.mark.django_db
def test_list_categories(authenticated_client):
    """Verify the category endpoint returns existing categories."""
    category = create_category(name="Fiction")

    response = authenticated_client.get("/api/v1/categories/")

    assert response.status_code == 200
    assert response.json()["data"][0]["uuid"] == str(category.uuid)
    assert response.json()["data"][0]["name"] == "Fiction"


@pytest.mark.django_db
def test_list_books(authenticated_client):
    """Verify the book endpoint returns existing catalog entries."""
    create_book()
    response = authenticated_client.get("/api/v1/books/")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
def test_get_and_soft_delete_book(authenticated_client):
    """Verify book details are available until the record is soft-deleted."""
    book = create_book()

    detail = authenticated_client.get(f"/api/v1/books/{book.uuid}/")
    deleted = authenticated_client.delete(f"/api/v1/books/{book.uuid}/")
    missing = authenticated_client.get(f"/api/v1/books/{book.uuid}/")

    assert detail.status_code == 200
    assert detail.json()["data"]["isbn"] == book.isbn
    assert deleted.status_code == 200
    assert missing.status_code == 404


@pytest.mark.django_db
def test_create_book_rejects_invalid_copy_counts(authenticated_client):
    """Verify available copies cannot exceed the total copy count."""
    category = create_category()
    response = authenticated_client.post(
        "/api/v1/books/",
        {
            "isbn": "9783333333333",
            "title": "Invalid Copies",
            "author": "Test Author",
            "category_uuid": str(category.uuid),
            "total_copies": 1,
            "available_copies": 2,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "available_copies" in response.json()["errors"]
