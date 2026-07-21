"""Serialization and validation for categories and books."""

from rest_framework import serializers

from services.models.book import Book
from services.models.category import Category


class BookCategorySerializer(serializers.ModelSerializer):
    """Serialize category identifiers and descriptive fields."""

    class Meta:
        """Configure category fields exposed by the API."""

        model = Category
        fields = ["uuid", "name", "description", "created_at"]
        read_only_fields = ["uuid", "created_at"]


class BookSerializer(serializers.ModelSerializer):
    """Serialize books and validate category and copy constraints."""

    category_uuid = serializers.UUIDField(write_only=True, required=False)
    category = BookCategorySerializer(read_only=True)

    class Meta:
        """Configure book fields and read-only values exposed by the API."""

        model = Book
        fields = [
            "uuid",
            "isbn",
            "title",
            "author",
            "category",
            "category_uuid",
            "publisher",
            "published_year",
            "description",
            "total_copies",
            "available_copies",
            "shelf_location",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "category", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validate category existence and consistent copy counts."""
        category_uuid = attrs.get("category_uuid")
        if self.instance is None and not category_uuid:
            raise serializers.ValidationError(
                {"category_uuid": "Category is required."}
            )
        if (
            category_uuid
            and not Category.objects.filter(
                uuid=category_uuid, deleted_at__isnull=True
            ).exists()
        ):
            raise serializers.ValidationError({"category_uuid": "Category not found."})

        available_copies = attrs.get(
            "available_copies", getattr(self.instance, "available_copies", None)
        )
        total_copies = attrs.get(
            "total_copies", getattr(self.instance, "total_copies", None)
        )
        if (
            available_copies is not None
            and total_copies is not None
            and available_copies > total_copies
        ):
            raise serializers.ValidationError(
                {"available_copies": "Available copies cannot exceed total copies."}
            )
        if total_copies is not None and total_copies <= 0:
            raise serializers.ValidationError(
                {"total_copies": "Total copies must be greater than zero."}
            )
        return attrs
