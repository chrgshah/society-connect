from django.db import models

from .base import BaseModel
from .book import Book
from .member import Member


class Lending(BaseModel):
    class Status(models.TextChoices):
        BORROWED = "BORROWED", "Borrowed"
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"

    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="lendings"
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="lendings")
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.BORROWED
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-borrowed_at"]
