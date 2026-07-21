"""HTTP controllers for category and book catalog operations."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView

from core.responses.mixins import ResponseMixin
from services.factories.category import CategoryFactory
from services.models.category import Category
from services.serializers.category import CategorySerializer
from services.shared.logger import logger
from services.shared.pagination import StandardPagination


class CategoryListController(ResponseMixin, GenericAPIView):
    """Search, paginate, and create categories."""

    serializer_class = CategorySerializer
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Category.objects.filter(deleted_at__isnull=True)

    def get(self, request):
        """Return a filtered page of non-deleted categories."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        return self.paginator.get_paginated_response(
            self.get_serializer(page, many=True).data,
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


class CategoryOptionsController(ResponseMixin, GenericAPIView):
    """Return an unpaginated category collection for remote dropdowns."""

    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Category.objects.filter(deleted_at__isnull=True).order_by("name")

    def get(self, request):
        categories = self.filter_queryset(self.get_queryset())[:50]
        return self.success_response(
            data=self.get_serializer(categories, many=True).data,
            message="Category options retrieved successfully.",
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
