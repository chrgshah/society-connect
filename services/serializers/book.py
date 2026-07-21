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

    category_uuid = serializers.UUIDField(write_only=True, required=True)
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
        if self.instance and "total_copies" in attrs:
            borrowed_copies = (
                self.instance.total_copies - self.instance.available_copies
            )
            if total_copies < borrowed_copies:
                raise serializers.ValidationError(
                    {
                        "total_copies": "Total copies cannot be less than currently borrowed copies."
                    }
                )
        return attrs

    def validate_category_uuid(self, value):
        if not Category.objects.filter(uuid=value).exists():
            raise serializers.ValidationError("Category not found.")
        return value

    def validate_published_year(self, value):
        from django.utils import timezone

        if value is not None and not 1000 <= value <= timezone.now().year:
            raise serializers.ValidationError("Enter a valid publication year.")
        return value

    def validate_isbn(self, value):
        normalized = value.replace("-", "").replace(" ", "").upper()
        valid_13 = normalized.isdigit() and len(normalized) == 13
        valid_10 = (
            len(normalized) == 10
            and normalized[:-1].isdigit()
            and normalized[-1] in "0123456789X"
        )
        if not (valid_10 or valid_13):
            raise serializers.ValidationError("Enter a valid ISBN-10 or ISBN-13.")
        return normalized
