"""Serialization and validation for categories."""

from rest_framework import serializers

from services.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serialize category identifiers and descriptive fields."""

    class Meta:
        """Configure category fields exposed by the API."""

        model = Category
        fields = ["uuid", "name", "description", "created_at"]
        read_only_fields = ["uuid", "created_at"]
