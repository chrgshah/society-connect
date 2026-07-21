"""Domain operations and query construction for books."""

from services.models.book import Book
from services.models.category import Category


class BookFactory:
    """Create, update, deactivate, and query book records."""

    @staticmethod
    def create_book(data):
        """Create a book linked to the category UUID in validated data."""
        category_uuid = data.pop("category_uuid", None)
        category = Category.objects.get(uuid=category_uuid) if category_uuid else None
        if category is None:
            raise ValueError("Category not found.")
        return Book.objects.create(category=category, **data)

    @staticmethod
    def update_book(book, data):
        """Apply validated fields and an optional category change to a book."""
        category_uuid = data.pop("category_uuid", None)
        if category_uuid:
            book.category = Category.objects.get(uuid=category_uuid)
        if "total_copies" in data and "available_copies" not in data:
            borrowed_copies = book.total_copies - book.available_copies
            data["available_copies"] = data["total_copies"] - borrowed_copies
        for key, value in data.items():
            setattr(book, key, value)
        book.save()
        return book

    @staticmethod
    def deactivate_book(book):
        """Mark a book inactive without deleting its record."""
        book.is_active = False
        book.save(update_fields=["is_active", "updated_at"])
        return book

    @staticmethod
    def get_queryset(
        search=None, author=None, category_uuid=None, is_available=None, is_active=None
    ):
        """Build a book queryset from optional catalog filters."""
        queryset = Book.objects.filter(deleted_at__isnull=True).select_related(
            "category"
        )
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(
                isbn__icontains=search
            )
        if author:
            queryset = queryset.filter(author__icontains=author)
        if category_uuid:
            queryset = queryset.filter(category__uuid=category_uuid)
        if is_available is not None:
            queryset = (
                queryset.filter(available_copies__gt=0)
                if is_available
                else queryset.filter(available_copies=0)
            )
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
