"""HTTP controllers for category and book catalog operations."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.book import BookFactory
from services.models.book import Book
from services.models.category import Category
from services.serializers.book import BookCategorySerializer, BookSerializer
from services.shared.logger import logger


class CategoryListController(ResponseMixin, APIView):
    """List active book categories."""

    def get(self, request):
        """Return categories ordered by display name."""
        categories = Category.objects.filter(deleted_at__isnull=True).order_by("name")
        return self.success_response(
            data=BookCategorySerializer(categories, many=True).data,
            message="Categories retrieved successfully.",
        )


class BookListController(ResponseMixin, APIView):
    """Search, paginate, and create books."""

    serializer_class = BookSerializer

    def get(self, request):
        """Return a filtered page of non-deleted books."""
        queryset = BookFactory.get_queryset(
            search=request.GET.get("search"),
            author=request.GET.get("author"),
            category_uuid=request.GET.get("category_uuid"),
            is_available=request.GET.get("is_available"),
            is_active=request.GET.get("is_active"),
        )
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])
        serializer = BookSerializer(items, many=True)
        return self.paginated_response(
            serializer.data,
            page,
            page_size,
            queryset.count(),
            message="Books retrieved successfully.",
        )

    def post(self, request):
        """Validate and create a book in the catalog."""
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = BookFactory.create_book(serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=book_created book_uuid=%s user_id=%s",
            book.uuid,
            request.user.id,
        )
        return self.success_response(
            data=BookSerializer(book).data,
            message="Book created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class BookDetailController(ResponseMixin, APIView):
    """Retrieve, modify, or deactivate an individual book."""

    serializer_class = BookSerializer

    def get(self, request, uuid):
        """Return one non-deleted book by UUID."""
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(
            data=BookSerializer(book).data, message="Book retrieved successfully."
        )

    def patch(self, request, uuid):
        """Apply a partial update to a book."""
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        serializer = BookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        book = BookFactory.update_book(book, serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=book_updated book_uuid=%s user_id=%s",
            book.uuid,
            request.user.id,
        )
        return self.success_response(
            data=BookSerializer(book).data, message="Book updated successfully."
        )

    def put(self, request, uuid):
        """Update a book using the endpoint's partial-update semantics."""
        return self.patch(request, uuid)

    def delete(self, request, uuid):
        """Soft-delete a book while retaining its historical data."""
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        book.soft_delete()
        logger.info(
            "[SOCIETY_CONNECT] event=book_deactivated book_uuid=%s user_id=%s",
            book.uuid,
            request.user.id,
        )
        return self.success_response(message="Book deactivated successfully.")
