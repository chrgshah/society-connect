"""HTTP controllers for category and book catalog operations."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.category import CategoryFactory
from services.models.category import Category
from services.serializers.category import CategorySerializer
from services.shared.logger import logger


class CategoryListController(ResponseMixin, APIView):
    """Search, paginate, and create categories."""

    serializer_class = CategorySerializer

    def get(self, request):
        """Return a filtered page of non-deleted categories."""
        queryset = CategoryFactory.get_queryset(
            search=request.GET.get("search"),
        )
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size
        items = list(queryset[start:end])
        serializer = CategorySerializer(items, many=True)
        return self.paginated_response(
            serializer.data,
            page,
            page_size,
            queryset.count(),
            message="Categories retrieved successfully.",
        )

    def post(self, request):
        """Validate and create a category."""
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = CategoryFactory.create_category(serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=category_created category_uuid=%s user_id=%s",
            category.uuid,
            request.user.id,
        )
        return self.success_response(
            data=CategorySerializer(category).data,
            message="Category created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CategoryDetailController(ResponseMixin, APIView):
    """Retrieve, modify, or deactivate an individual category."""

    serializer_class = CategorySerializer

    def get(self, request, uuid):
        """Return one non-deleted category by UUID."""
        category = get_object_or_404(Category, uuid=uuid, deleted_at__isnull=True)
        return self.success_response(
            data=CategorySerializer(category).data,
            message="Category retrieved successfully.",
        )

    def patch(self, request, uuid):
        """Apply a partial update to a category."""
        category = get_object_or_404(Category, uuid=uuid, deleted_at__isnull=True)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = CategoryFactory.update_category(category, serializer.validated_data)
        logger.info(
            "[SOCIETY_CONNECT] event=category_updated category_uuid=%s user_id=%s",
            category.uuid,
            request.user.id,
        )
        return self.success_response(
            data=CategorySerializer(category).data,
            message="Category updated successfully.",
        )

    def put(self, request, uuid):
        """Update a category using the endpoint's partial-update semantics."""
        return self.patch(request, uuid)

    def delete(self, request, uuid):
        """Soft-delete a category while retaining its historical data."""
        category = get_object_or_404(Category, uuid=uuid, deleted_at__isnull=True)
        category.soft_delete()
        logger.info(
            "[SOCIETY_CONNECT] event=category_deactivated category_uuid=%s user_id=%s",
            category.uuid,
            request.user.id,
        )
        return self.success_response(message="Category deactivated successfully.")
