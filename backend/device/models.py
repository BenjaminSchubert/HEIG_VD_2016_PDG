"""Contains all models from the `device` module."""

from django.db import models
from django.db.models import Q

from device.fcm import send_fcm_message
from user.models import User

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeviceManager(models.Manager):
    """Overrides the default Manager with our custom one."""


class Device(models.Model):
    """Extends `Model` to keep information about devices."""

    registration_id = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User)

    objects = DeviceManager()

    def send_push(self, title=None, body=None, **kwargs):
        result = send_fcm_message(
            registration_id=self.registration_id,
            title=title,
            body=body,
            **kwargs
        )

        if "error" in result["results"][0]:  # TODO : handle deferred
            self.active = False

        return result

    def save(self, *args, **kwargs):

        Device.objects.filter(Q(registration_id=self.registration_id) | Q(user=self.u)).delete()

        super(Device, self).save(*args, **kwargs)
