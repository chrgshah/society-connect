"""Aggregate queries used by the management dashboard."""

from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, time, timedelta

from services.models.book import Book
from services.models.lending import Lending
from services.models.member import Member


class DashboardFactory:
    """Calculate summary metrics across books, members, and lendings."""

    @staticmethod
    def get_summary(from_date, to_date):
        """Return catalog, member, availability, and overdue counts for a range."""
        start_at = timezone.make_aware(datetime.combine(from_date, time.min))
        end_at = timezone.make_aware(
            datetime.combine(to_date + timedelta(days=1), time.min)
        )
        created_range = {"created_at__gte": start_at, "created_at__lt": end_at}
        book_totals = Book.objects.filter(
            deleted_at__isnull=True, **created_range
        ).aggregate(
            total_books=Count("id"),
            total_copies=Sum("total_copies", default=0),
            available_copies=Sum("available_copies", default=0),
        )
        total_books = book_totals["total_books"]
        total_copies = book_totals["total_copies"]
        available_copies = book_totals["available_copies"]
        borrowed_copies = total_copies - available_copies
        member_totals = Member.objects.filter(
            deleted_at__isnull=True, **created_range
        ).aggregate(
            total_members=Count("id"),
            active_members=Count("id", filter=Q(is_active=True)),
        )
        total_members = member_totals["total_members"]
        active_members = member_totals["active_members"]
        overdue_borrowings = Lending.objects.filter(
            deleted_at__isnull=True,
            status=Lending.Status.OVERDUE,
            borrowed_at__gte=start_at,
            borrowed_at__lt=end_at,
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
