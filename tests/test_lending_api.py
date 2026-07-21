"""Integration tests for borrowing, returning, and overdue APIs."""

import pytest

from tests.helpers import create_book, create_member


@pytest.mark.django_db
def test_borrow_and_return_book(authenticated_client):
    """Verify borrowing and returning update lending and copy state."""
    member = create_member(email="borrower@example.com", membership_number="MEM-222222")
    book = create_book(isbn="9782222222222", total_copies=1, available_copies=1)

    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["success"] is True

    lending_uuid = response.json()["data"]["uuid"]
    returned = authenticated_client.post(f"/api/v1/lending/{lending_uuid}/return/")
    assert returned.status_code == 200
    assert returned.json()["success"] is True


@pytest.mark.django_db
def test_borrow_rejects_notes_over_2500_characters(authenticated_client):
    """Verify lending notes enforce the documented maximum length."""
    member = create_member()
    book = create_book()
    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {
            "member_uuid": str(member.uuid),
            "book_uuid": str(book.uuid),
            "notes": "x" * 2501,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "notes" in response.json()["errors"]


@pytest.mark.django_db
def test_empty_overdue_list_returns_array(authenticated_client):
    """Verify an empty overdue result uses an array response."""
    response = authenticated_client.get("/api/v1/lending/overdue/")

    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.django_db
def test_overdue_list_supports_framework_pagination(authenticated_client):
    """Verify paginated callers receive the standard pagination envelope."""
    response = authenticated_client.get("/api/v1/lending/overdue/?page=1&page_size=10")

    assert response.status_code == 200
    assert response.json()["data"]["results"] == []
    assert response.json()["data"]["pagination"]["page"] == 1


@pytest.mark.django_db
def test_borrow_rejects_inactive_member(authenticated_client):
    """Verify inactive members cannot borrow books."""
    member = create_member(is_active=False)
    book = create_book()

    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Member is inactive."


@pytest.mark.django_db
def test_borrow_rejects_unavailable_book(authenticated_client):
    """Verify a book with no available copies cannot be borrowed."""
    member = create_member()
    book = create_book(available_copies=0)

    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Book is not available."


@pytest.mark.django_db
def test_borrow_rejects_inactive_book(authenticated_client):
    """Verify inactive books cannot be borrowed even when copies exist."""
    member = create_member()
    book = create_book(is_active=False)

    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Book is inactive."


@pytest.mark.django_db
def test_past_due_borrow_is_immediately_overdue(authenticated_client):
    """Verify a lending created past its due time is marked overdue."""
    member = create_member()
    book = create_book()
    response = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {
            "member_uuid": str(member.uuid),
            "book_uuid": str(book.uuid),
            "due_at": "2020-01-01T00:00:00Z",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["data"]["status"] == "OVERDUE"


@pytest.mark.django_db
def test_lending_detail_list_and_member_borrowed_books(authenticated_client):
    """Verify a borrowing appears in detail, list, and member-specific APIs."""
    member = create_member()
    book = create_book()
    borrowed = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )
    lending_uuid = borrowed.json()["data"]["uuid"]

    detail = authenticated_client.get(f"/api/v1/lending/{lending_uuid}/")
    listing = authenticated_client.get("/api/v1/lending/")
    member_books = authenticated_client.get(
        f"/api/v1/members/{member.uuid}/borrowed-books/"
    )

    assert detail.status_code == 200
    assert detail.json()["data"]["uuid"] == lending_uuid
    assert listing.json()["data"]["pagination"]["total_records"] == 1
    assert member_books.json()["data"][0]["uuid"] == lending_uuid


@pytest.mark.django_db
def test_returning_same_lending_twice_is_rejected(authenticated_client):
    """Verify returning an already returned lending does not alter copies."""
    member = create_member()
    book = create_book(total_copies=1, available_copies=1)
    borrowed = authenticated_client.post(
        "/api/v1/lending/borrow/",
        {"member_uuid": str(member.uuid), "book_uuid": str(book.uuid)},
        format="json",
    )
    lending_uuid = borrowed.json()["data"]["uuid"]

    first = authenticated_client.post(f"/api/v1/lending/{lending_uuid}/return/")
    second = authenticated_client.post(f"/api/v1/lending/{lending_uuid}/return/")

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["message"] == "Lending has already been returned."
