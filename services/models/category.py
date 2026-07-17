"""Book category model."""

from django.db import models

from .base import BaseModel


class Category(BaseModel):
    """Group books under a unique category name."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        """Order categories by name by default."""

        ordering = ["name"]
