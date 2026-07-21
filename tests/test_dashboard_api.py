"""Integration tests for dashboard summary metrics."""

from datetime import timedelta

import pytest
from django.utils import timezone

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


@pytest.mark.django_db
def test_dashboard_date_range_filters_stats_and_lendings(authenticated_client):
    """Apply the same reporting window to every dashboard aggregate."""
    recent_book = create_book(isbn="9780000000100", total_copies=2)
    old_book = create_book(
        isbn="9780000000101", category=recent_book.category, total_copies=5
    )
    recent_member = create_member(email="recent@example.com")
    old_member = create_member(email="old@example.com", membership_number="MEM-OLD")
    old_date = timezone.now() - timedelta(days=10)
    recent_book.__class__.objects.filter(pk=old_book.pk).update(created_at=old_date)
    recent_member.__class__.objects.filter(pk=old_member.pk).update(created_at=old_date)

    today = timezone.localdate()
    response = authenticated_client.get(
        "/api/v1/dashboard/summary/",
        {"from_date": today - timedelta(days=6), "to_date": today},
    )

    assert response.status_code == 200
    assert response.json()["data"]["total_books"] == 1
    assert response.json()["data"]["total_copies"] == 2
    assert response.json()["data"]["total_members"] == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {"from_date": "2025-01-01", "to_date": "2025-08-01"},
        {"from_date": "2025-08-02", "to_date": "2025-08-01"},
        {"from_date": "2099-01-01", "to_date": "2099-01-02"},
    ],
)
def test_dashboard_rejects_invalid_date_ranges(authenticated_client, params):
    """Reject ranges over six months, reversed ranges, and future dates."""
    response = authenticated_client.get("/api/v1/dashboard/summary/", params)

    assert response.status_code == 400


@pytest.mark.django_db
def test_lending_list_rejects_range_over_six_months(authenticated_client):
    """Enforce the dashboard range limit on its lending-table query too."""
    response = authenticated_client.get(
        "/api/v1/lending/",
        {"from_date": "2025-01-01", "to_date": "2025-08-01"},
    )

    assert response.status_code == 400
