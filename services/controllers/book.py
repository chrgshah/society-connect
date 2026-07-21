"""HTTP controllers for category and book catalog operations."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from core.exceptions.exceptions import ActiveLendingError
from core.responses.mixins import ResponseMixin
from services.factories.book import BookFactory
from services.models.book import Book
from services.serializers.book import BookSerializer
from services.shared.logger import logger
from services.shared.filters import BookFilter
from services.shared.pagination import StandardPagination


class BookListController(ResponseMixin, GenericAPIView):
    """Search, paginate, and create books."""

    serializer_class = BookSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "isbn", "author", "publisher"]
    ordering_fields = ["title", "author", "created_at", "available_copies"]
    ordering = ["title"]

    def get_queryset(self):
        return Book.objects.filter(deleted_at__isnull=True).select_related("category")

    def get(self, request):
        """Return a filtered page of non-deleted books."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        return self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data,
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


class BookOptionsController(ResponseMixin, GenericAPIView):
    """Return a compact, unpaginated book collection for remote dropdowns."""

    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "isbn", "author"]

    def get_queryset(self):
        return (
            Book.objects.filter(
                deleted_at__isnull=True,
                is_active=True,
                available_copies__gt=0,
            )
            .select_related("category")
            .order_by("title")
        )

    def get(self, request):
        books = self.filter_queryset(self.get_queryset())[:50]
        return self.success_response(
            data=self.get_serializer(books, many=True).data,
            message="Book options retrieved successfully.",
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
        if book.lendings.filter(
            deleted_at__isnull=True, status__in=["BORROWED", "OVERDUE"]
        ).exists():
            raise ActiveLendingError(
                "A book with active lendings cannot be deactivated."
            )
        book.soft_delete()
        logger.info(
            "[SOCIETY_CONNECT] event=book_deactivated book_uuid=%s user_id=%s",
            book.uuid,
            request.user.id,
        )
        return self.success_response(message="Book deactivated successfully.")
