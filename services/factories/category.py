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
