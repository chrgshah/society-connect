"""Society member model."""

from django.db import models

from .base import BaseModel


class Member(BaseModel):
    """Represent a registered person eligible to borrow books."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    membership_number = models.CharField(max_length=30, unique=True)
    membership_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        """Show recently created members first by default."""

        ordering = ["-created_at"]

    @property
    def full_name(self):
        """Return the member's first and last names as display text."""
        return f"{self.first_name} {self.last_name}".strip()
