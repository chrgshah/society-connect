import uuid

from django.db.models.signals import pre_save
from django.dispatch import receiver

from services.models.base import BaseModel


@receiver(pre_save, sender=BaseModel)
def ensure_uuid(sender, instance, **kwargs):
    if not instance.uuid:
        instance.uuid = uuid.uuid4()
