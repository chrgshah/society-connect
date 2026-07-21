"""Aggregate queries used by the management dashboard."""

from django.db.models import Count, Q, Sum

from services.models.book import Book
from services.models.lending import Lending
from services.models.member import Member


class DashboardFactory:
    """Calculate summary metrics across books, members, and lendings."""

    @staticmethod
    def get_summary():
        """Return current catalog, member, availability, and overdue counts."""
        book_totals = Book.objects.filter(deleted_at__isnull=True).aggregate(
            total_books=Count("id"),
            total_copies=Sum("total_copies", default=0),
            available_copies=Sum("available_copies", default=0),
        )
        total_books = book_totals["total_books"]
        total_copies = book_totals["total_copies"]
        available_copies = book_totals["available_copies"]
        borrowed_copies = total_copies - available_copies
        member_totals = Member.objects.filter(deleted_at__isnull=True).aggregate(
            total_members=Count("id"),
            active_members=Count("id", filter=Q(is_active=True)),
        )
        total_members = member_totals["total_members"]
        active_members = member_totals["active_members"]
        overdue_borrowings = Lending.objects.filter(
            deleted_at__isnull=True, status=Lending.Status.OVERDUE
        ).count()
        return {
            "total_books": total_books,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "borrowed_copies": borrowed_copies,
            "total_members": total_members,
            "active_members": active_members,
            "overdue_borrowings": overdue_borrowings,
        }
