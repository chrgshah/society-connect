"""Signal handlers that maintain shared model fields."""

import uuid

from django.db.models.signals import pre_save
from django.dispatch import receiver

from services.models.base import BaseModel


@receiver(pre_save, sender=BaseModel)
def ensure_uuid(sender, instance, **kwargs):
    """Assign a UUID before saving a base model that lacks one."""
    if not instance.uuid:
        instance.uuid = uuid.uuid4()
