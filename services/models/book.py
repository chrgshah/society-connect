from django.db import models

from .base import BaseModel
from .category import Category


class Book(BaseModel):
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
        ordering = ["title"]
