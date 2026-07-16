from services.models.book import Book
from services.models.category import Category


class BookFactory:
    @staticmethod
    def create_book(data):
        category_uuid = data.pop("category_uuid", None)
        category = Category.objects.get(uuid=category_uuid) if category_uuid else None
        if category is None:
            raise ValueError("Category not found.")
        return Book.objects.create(category=category, **data)

    @staticmethod
    def update_book(book, data):
        category_uuid = data.pop("category_uuid", None)
        if category_uuid:
            book.category = Category.objects.get(uuid=category_uuid)
        for key, value in data.items():
            setattr(book, key, value)
        book.save()
        return book

    @staticmethod
    def deactivate_book(book):
        book.is_active = False
        book.save(update_fields=["is_active", "updated_at"])
        return book

    @staticmethod
    def get_queryset(
        search=None, author=None, category_uuid=None, is_available=None, is_active=None
    ):
        queryset = Book.objects.filter(deleted_at__isnull=True)
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
