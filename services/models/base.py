"""Abstract model fields and soft-deletion behavior shared by services."""

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Return only records that have not been soft-deleted."""

    def get_queryset(self):
        """Apply the active-record constraint to every query."""
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """Provide UUIDs, timestamps, and soft deletion to domain models."""

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, db_index=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        """Prevent Django from creating a table for this base class."""

        abstract = True

    def save(self, *args, **kwargs):
        """Ensure a UUID exists before persisting the model."""
        if not self.uuid:
            import uuid

            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        """Timestamp the record as deleted without removing it permanently."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])

    @property
    def is_deleted(self) -> bool:
        """Return whether the model has been soft-deleted."""
        return self.deleted_at is not None
