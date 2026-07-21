"""Book lending history model."""

from django.db import models

from .base import BaseModel
from .book import Book
from .member import Member


class Lending(BaseModel):
    """Track a borrowed book through its return lifecycle."""

    class Status(models.TextChoices):
        """Supported lifecycle states for a lending."""

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
        """Show the newest borrowings first by default."""

        ordering = ["-borrowed_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(status="RETURNED", returned_at__isnull=False)
                    | models.Q(
                        status__in=["BORROWED", "OVERDUE"], returned_at__isnull=True
                    )
                ),
                name="lending_return_state_consistent",
            )
        ]
