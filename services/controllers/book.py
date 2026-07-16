from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.book import BookFactory
from services.models.author import Author
from services.models.book import Book
from services.models.category import Category
from services.serializers.book import BookSerializer


class BookListController(ResponseMixin, APIView):
    def get(self, request):
        queryset = BookFactory.get_queryset(
            search=request.GET.get("search"),
            author_uuid=request.GET.get("author_uuid"),
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
        return self.paginated_response(serializer.data, page, page_size, queryset.count(), message="Books retrieved successfully.")

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = BookFactory.create_book(serializer.validated_data)
        return self.success_response(data=BookSerializer(book).data, message="Book created successfully.", status_code=status.HTTP_201_CREATED)


class BookDetailController(ResponseMixin, APIView):
    def get(self, request, uuid):
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(data=BookSerializer(book).data, message="Book retrieved successfully.")

    def patch(self, request, uuid):
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        serializer = BookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        book = BookFactory.update_book(book, serializer.validated_data)
        return self.success_response(data=BookSerializer(book).data, message="Book updated successfully.")

    def put(self, request, uuid):
        return self.patch(request, uuid)

    def delete(self, request, uuid):
        book = get_object_or_404(Book, uuid=uuid, deleted_at__isnull=True)
        book.soft_delete()
        return self.success_response(message="Book deactivated successfully.")
