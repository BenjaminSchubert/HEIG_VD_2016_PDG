"""Contains all signal handlers from the `device` module."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from device.models import Device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(post_save, sender=Device)
def post_save_device(instance, **kwargs):
    """
    Fired after a device is saved.

    Try to send eventually deferred messages to the user who registered the device.
    """
    instance.user.send_deferred_messages()
