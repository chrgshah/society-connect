"""Unit tests for shared helpers and factory branches not covered by APIs."""

import pytest
from django.db.models import Q

from services.factories.book import BookFactory
from services.factories.member import MemberFactory
from services.models.user import User
from services.shared.filters import build_search_filter
from services.shared.permissions import IsStaffUser
from tests.helpers import create_book, create_member


def test_build_search_filter_handles_empty_and_multiple_terms():
    """Verify search terms are combined across all configured model fields."""
    assert build_search_filter("", ["title"]) is None

    query = build_search_filter("django guide", ["title", "author"])

    assert isinstance(query, Q)
    assert query.children


def test_staff_permission_requires_authenticated_active_user():
    """Verify the custom permission accepts only active authenticated users."""
    permission = IsStaffUser()
    active_user = type(
        "ActiveUser", (), {"is_authenticated": True, "is_active": True}
    )()
    inactive_user = type(
        "InactiveUser", (), {"is_authenticated": True, "is_active": False}
    )()

    assert permission.has_permission(type("Request", (), {"user": active_user})(), None)
    assert not permission.has_permission(
        type("Request", (), {"user": inactive_user})(), None
    )


@pytest.mark.django_db
def test_user_manager_rejects_missing_required_fields():
    """Verify user creation rejects each missing identity or credential field."""
    with pytest.raises(ValueError, match="username"):
        User.objects.create_user("", "user@example.com", "password")
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user("user", "", "password")
    with pytest.raises(ValueError, match="password"):
        User.objects.create_user("user", "user@example.com", None)


@pytest.mark.django_db
def test_book_factory_filters_and_deactivates_books():
    """Verify book query filters and explicit deactivation behavior."""
    book = create_book(author="Jane Author", available_copies=1)

    assert BookFactory.get_queryset(search="Test").get() == book
    assert BookFactory.get_queryset(author="Jane").get() == book
    assert BookFactory.get_queryset(is_available=True).get() == book

    BookFactory.deactivate_book(book)

    assert book.is_active is False
    assert BookFactory.get_queryset(is_active=False).get() == book


@pytest.mark.django_db
def test_member_factory_filters_deactivates_and_generates_number():
    """Verify member status filtering, deactivation, and number generation."""
    member = create_member(first_name="Searchable")

    assert MemberFactory.get_queryset(search="Searchable").get() == member
    assert MemberFactory.get_queryset(is_active=True).get() == member

    MemberFactory.deactivate_member(member)

    assert member.is_active is False
    assert MemberFactory.get_queryset(is_active=False).get() == member
    expected_number = f"MEM-{member.id + 1:06d}"
    assert MemberFactory._generate_membership_number() == expected_number
