"""Tests for serializer validation and lending filter branches."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone
from rest_framework import serializers

from services.factories.lending import LendingFactory
from services.models.lending import Lending
from services.serializers.book import BookSerializer
from services.serializers.member import MemberSerializer
from services.serializers.lending import BorrowBookSerializer
from services.serializers.authentication import LoginSerializer
from services.shared.filters import BookFilter
from tests.helpers import create_book, create_member


@pytest.mark.django_db
def test_book_serializer_rejects_missing_or_unknown_category():
    """Verify book creation requires an existing category UUID."""
    missing = BookSerializer(data={"isbn": "1", "title": "Book", "author": "Author"})
    unknown = BookSerializer(
        data={
            "isbn": "2",
            "title": "Book",
            "author": "Author",
            "category_uuid": uuid4(),
        }
    )

    assert not missing.is_valid()
    assert "category_uuid" in missing.errors
    assert not unknown.is_valid()
    assert "category_uuid" in unknown.errors


@pytest.mark.django_db
def test_book_serializer_rejects_nonpositive_copy_values():
    """Verify total and available copy counts cannot be invalid."""
    book = create_book()
    total = BookSerializer(
        book,
        data={"total_copies": 0, "available_copies": 0},
        partial=True,
    )
    available = BookSerializer(book, data={"available_copies": -1}, partial=True)

    assert not total.is_valid()
    assert "total_copies" in total.errors
    assert not available.is_valid()
    assert "available_copies" in available.errors


@pytest.mark.django_db
def test_book_serializer_rejects_negative_available_without_instance():
    """Verify negative availability reaches its dedicated validation branch."""
    book = create_book()
    serializer = BookSerializer(
        book,
        data={"total_copies": 2, "available_copies": -1},
        partial=True,
    )
    assert not serializer.is_valid()
    assert "available_copies" in serializer.errors


@pytest.mark.django_db
def test_book_serializer_rejects_invalid_year_and_borrowed_copy_reduction():
    """Verify publication years and reductions below borrowed stock are rejected."""
    book = create_book(total_copies=3, available_copies=1)
    invalid_year = BookSerializer(book, data={"published_year": 999}, partial=True)
    invalid_total = BookSerializer(book, data={"total_copies": 1}, partial=True)

    assert not invalid_year.is_valid()
    assert "published_year" in invalid_year.errors
    assert not invalid_total.is_valid()
    assert "total_copies" in invalid_total.errors


@pytest.mark.django_db
def test_borrow_serializer_rejects_unknown_relationships():
    """Turn missing member and book identifiers into field validation errors."""
    serializer = BorrowBookSerializer(
        data={"member_uuid": uuid4(), "book_uuid": uuid4()}
    )

    assert not serializer.is_valid()
    assert set(serializer.errors) == {"member_uuid", "book_uuid"}


def test_member_serializer_rejects_overlong_phone_number():
    """Reject phone values beyond the international 15-digit limit."""
    with pytest.raises(serializers.ValidationError):
        MemberSerializer().validate_phone("+1234567890123456")


@pytest.mark.django_db
def test_book_availability_filter_handles_unspecified_value():
    """Leave a queryset unchanged when availability was not supplied."""
    queryset = create_book().__class__.objects.all()
    filtered = BookFilter().filter_availability(queryset, "is_available", None)

    assert filtered is queryset


@pytest.mark.django_db
def test_book_availability_filter_handles_both_boolean_values():
    """Apply available and unavailable dropdown/list filters."""
    available = create_book(isbn="9780000000018", available_copies=1)
    unavailable = create_book(
        isbn="9780000000025", category=available.category, available_copies=0
    )
    queryset = available.__class__.objects.all()
    book_filter = BookFilter()

    assert list(book_filter.filter_availability(queryset, "is_available", True)) == [
        available
    ]
    assert list(book_filter.filter_availability(queryset, "is_available", False)) == [
        unavailable
    ]


@pytest.mark.django_db
def test_member_serializer_unique_fields_allow_current_instance():
    """Verify uniqueness checks permit unchanged values and reject duplicates."""
    member = create_member()
    current = MemberSerializer(member, data={"email": member.email}, partial=True)
    assert current.is_valid(), current.errors

    duplicate = MemberSerializer(
        data={
            "first_name": "Other",
            "last_name": "Member",
            "email": "other@example.com",
            "phone": "+1234567890",
            "membership_number": member.membership_number,
            "membership_date": "2024-01-01",
        }
    )
    assert not duplicate.is_valid()
    assert "membership_number" in duplicate.errors

    duplicate_email = MemberSerializer(
        data={
            "first_name": "Other",
            "last_name": "Member",
            "email": member.email,
            "phone": "+1234567890",
            "membership_number": "MEM-UNIQUE",
            "membership_date": "2024-01-01",
        }
    )
    assert not duplicate_email.is_valid()
    assert "email" in duplicate_email.errors

    validator = MemberSerializer()
    with pytest.raises(serializers.ValidationError):
        validator.validate_email(member.email)
    with pytest.raises(serializers.ValidationError):
        validator.validate_membership_number(member.membership_number)


@pytest.mark.django_db
def test_login_serializer_rejects_unknown_user():
    """Verify login does not disclose when a username does not exist."""
    serializer = LoginSerializer(data={"username": "unknown", "password": "wrong"})
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors


@pytest.mark.django_db
def test_lending_queryset_applies_all_filters():
    """Verify every supported lending filter selects a matching record."""
    member = create_member(first_name="Filterable")
    book = create_book(title="Filter Book")
    lending = Lending.objects.create(
        member=member,
        book=book,
        due_at=timezone.now() + timedelta(days=1),
        notes="searchable note",
    )
    borrowed_date = lending.borrowed_at.date().isoformat()

    queryset = LendingFactory.get_queryset(
        search="searchable",
        status=Lending.Status.BORROWED,
        member_uuid=member.uuid,
        book_uuid=book.uuid,
        from_date=borrowed_date,
        to_date=borrowed_date,
    )

    assert queryset.get() == lending
