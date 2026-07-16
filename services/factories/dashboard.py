from services.models.book import Book
from services.models.lending import Lending
from services.models.member import Member


class DashboardFactory:
    @staticmethod
    def get_summary():
        total_books = Book.objects.filter(deleted_at__isnull=True).count()
        total_copies = sum(
            book.total_copies for book in Book.objects.filter(deleted_at__isnull=True)
        )
        available_copies = sum(
            book.available_copies
            for book in Book.objects.filter(deleted_at__isnull=True)
        )
        borrowed_copies = total_copies - available_copies
        total_members = Member.objects.filter(deleted_at__isnull=True).count()
        active_members = Member.objects.filter(
            deleted_at__isnull=True, is_active=True
        ).count()
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
