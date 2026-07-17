"""Integration tests for dashboard summary metrics."""

import pytest

from services.models.lending import Lending
from tests.helpers import create_book, create_member


@pytest.mark.django_db
def test_dashboard_summary_returns_current_totals(authenticated_client):
    """Verify dashboard counters reflect current books and members."""
    category_book = create_book(total_copies=3, available_copies=2)
    create_member()
    Lending.objects.create(
        member=create_member(
            email="borrower@example.com", membership_number="MEM-000002"
        ),
        book=category_book,
        due_at="2024-01-01T00:00:00Z",
        status=Lending.Status.OVERDUE,
    )

    response = authenticated_client.get("/api/v1/dashboard/summary/")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_books": 1,
        "total_copies": 3,
        "available_copies": 2,
        "borrowed_copies": 1,
        "total_members": 2,
        "active_members": 2,
        "overdue_borrowings": 1,
    }
