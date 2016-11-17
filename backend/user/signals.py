"""Contains all signal handlers from the `users` module."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(pre_save, sender=FCMDevice)
def create_device(instance, **kwargs):
    """
    Fired when a new device is created.

    It remove eventual devices already attached to the current logged in user.
    """
    FCMDevice.objects.filter(user_id=instance.user_id).delete()
