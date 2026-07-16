from django.db import models

from .base import BaseModel


class Author(BaseModel):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["name"]
