"""Factory helpers that create common model records in tests."""

from services.models.category import Category
from services.models.member import Member
from services.models.book import Book


def create_category(**kwargs):
    """Create a category with overridable defaults."""
    defaults = {"name": "Test Category", "description": "Demo"}
    defaults.update(kwargs)
    return Category.objects.create(**defaults)


def create_member(**kwargs):
    """Create a member with overridable defaults."""
    defaults = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone": "+1234567890",
        "address": "123 Main",
        "membership_number": "MEM-000001",
        "membership_date": "2024-01-02",
        "is_active": True,
    }
    defaults.update(kwargs)
    return Member.objects.create(**defaults)


def create_book(**kwargs):
    """Create a book and category with overridable defaults."""
    author = kwargs.pop("author", "Test Author")
    category = kwargs.pop("category", None) or create_category()
    defaults = {
        "isbn": "9780000000001",
        "title": "Test Book",
        "publisher": "Example Press",
        "published_year": 2020,
        "description": "Demo",
        "total_copies": 2,
        "available_copies": 2,
        "shelf_location": "A1",
        "is_active": True,
    }
    defaults.update(kwargs)
    return Book.objects.create(author=author, category=category, **defaults)
