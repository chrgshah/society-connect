from django.core.validators import EmailValidator
from django.db import models

from .base import BaseModel


class Member(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    membership_number = models.CharField(max_length=30, unique=True)
    membership_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
