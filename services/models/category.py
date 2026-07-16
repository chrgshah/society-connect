from django.db import models

from .base import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
