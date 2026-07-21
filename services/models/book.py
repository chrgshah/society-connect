"""Book catalog model."""

from django.db import models

from .base import BaseModel
from .category import Category


class Book(BaseModel):
    """Represent a catalog title and its copy availability."""

    isbn = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="books"
    )
    publisher = models.CharField(max_length=255, blank=True)
    published_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        """Order catalog results by title by default."""

        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"], name="book_title_idx"),
            models.Index(fields=["author"], name="book_author_idx"),
            models.Index(fields=["publisher"], name="book_publisher_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_copies__gt=0),
                name="book_total_copies_positive",
            ),
            models.CheckConstraint(
                check=models.Q(available_copies__lte=models.F("total_copies")),
                name="book_available_not_above_total",
            ),
        ]
