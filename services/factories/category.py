"""Domain operations and query construction for categories."""

from services.models.category import Category


class CategoryFactory:
    """Create, update, and query category records."""

    @staticmethod
    def create_category(data):
        """Create a category with the provided data."""
        return Category.objects.create(**data)

    @staticmethod
    def update_category(category, data):
        """Update a category with the provided data."""
        for key, value in data.items():
            setattr(category, key, value)
        category.save()
        return category

    @staticmethod
    def get_queryset(search=None):
        """Build a category queryset from optional filters."""
        queryset = Category.objects.filter(deleted_at__isnull=True)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
