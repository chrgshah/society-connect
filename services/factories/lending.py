"""Transactional domain operations and queries for book lending."""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from core.exceptions.exceptions import (
    BookNotAvailableError,
    InactiveBookError,
    InactiveMemberError,
    LendingAlreadyReturnedError,
)
from services.models.book import Book
from services.models.lending import Lending
from services.models.member import Member
from services.shared.logger import logger


class LendingFactory:
    """Manage borrowing, returns, and lending record retrieval."""

    @staticmethod
    @transaction.atomic
    def borrow_book(member_uuid, book_uuid, due_at=None, notes=""):
        """Atomically lend an available book to an eligible member."""
        member = Member.objects.select_for_update().get(uuid=member_uuid)
        book = Book.objects.select_for_update().get(uuid=book_uuid)
        if not member.is_active:
            logger.warning(
                "[SOCIETY_CONNECT] event=borrow_rejected reason=inactive_member "
                "member_uuid=%s book_uuid=%s",
                member_uuid,
                book_uuid,
            )
            raise InactiveMemberError()
        if not book.is_active:
            logger.warning(
                "[SOCIETY_CONNECT] event=borrow_rejected reason=inactive_book "
                "member_uuid=%s book_uuid=%s",
                member_uuid,
                book_uuid,
            )
            raise InactiveBookError()
        if book.available_copies <= 0:
            logger.warning(
                "[SOCIETY_CONNECT] event=borrow_rejected reason=unavailable "
                "member_uuid=%s book_uuid=%s",
                member_uuid,
                book_uuid,
            )
            raise BookNotAvailableError()
        due_at = due_at or timezone.now() + timedelta(days=14)
        lending = Lending.objects.create(
            member=member, book=book, due_at=due_at, notes=notes
        )
        book.available_copies -= 1
        book.save(update_fields=["available_copies", "updated_at"])
        if lending.status == Lending.Status.BORROWED:
            if lending.due_at < timezone.now():
                lending.status = Lending.Status.OVERDUE
                lending.save(update_fields=["status", "updated_at"])
        logger.info(
            "[SOCIETY_CONNECT] event=book_borrowed lending_uuid=%s "
            "member_uuid=%s book_uuid=%s",
            lending.uuid,
            member_uuid,
            book_uuid,
        )
        return lending

    @staticmethod
    @transaction.atomic
    def return_book(lending_uuid):
        """Atomically return a lending and restore book availability."""
        lending = Lending.objects.select_for_update().get(uuid=lending_uuid)
        book = Book.objects.select_for_update().get(pk=lending.book_id)
        if lending.status == Lending.Status.RETURNED:
            logger.warning(
                "[SOCIETY_CONNECT] event=return_rejected reason=already_returned "
                "lending_uuid=%s",
                lending_uuid,
            )
            raise LendingAlreadyReturnedError()
        lending.returned_at = timezone.now()
        lending.status = Lending.Status.RETURNED
        lending.save(update_fields=["returned_at", "status", "updated_at"])
        book.available_copies = min(book.total_copies, book.available_copies + 1)
        book.save(update_fields=["available_copies", "updated_at"])
        logger.info(
            "[SOCIETY_CONNECT] event=book_returned lending_uuid=%s book_uuid=%s",
            lending.uuid,
            book.uuid,
        )
        return lending

    @staticmethod
    def get_queryset(
        search=None,
        status=None,
        member_uuid=None,
        book_uuid=None,
        from_date=None,
        to_date=None,
    ):
        """Build a lending queryset from optional search and date filters."""
        queryset = Lending.objects.select_related("member", "book")
        if search:
            queryset = (
                queryset.filter(notes__icontains=search)
                | queryset.filter(member__first_name__icontains=search)
                | queryset.filter(book__title__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if member_uuid:
            queryset = queryset.filter(member__uuid=member_uuid)
        if book_uuid:
            queryset = queryset.filter(book__uuid=book_uuid)
        if from_date:
            queryset = queryset.filter(borrowed_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(borrowed_at__date__lte=to_date)
        return queryset

    @staticmethod
    def get_member_borrowed_books(member_uuid):
        """Return the member's lending records still marked as borrowed."""
        return Lending.objects.filter(
            member__uuid=member_uuid,
            status=Lending.Status.BORROWED,
        ).select_related("member", "book")

    @staticmethod
    def get_overdue_records():
        """Return unreturned lendings whose due date is in the past."""
        now = timezone.now()
        return (
            Lending.objects.filter(
                status__in=[Lending.Status.BORROWED, Lending.Status.OVERDUE],
                due_at__lt=now,
            )
            .select_related("member", "book")
            .order_by("-due_at")
        )
