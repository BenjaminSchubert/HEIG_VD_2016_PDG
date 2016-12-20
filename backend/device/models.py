"""Contains all models from the `device` module."""

from django.db import models
from django.db import transaction
from django.conf import settings

from device.fcm import send_fcm_message

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class Device(models.Model):
    """
    Extends `Model` to keep information about devices.

    Device has a One to One relation. The foreign key is located on the device
    to allow eventually mutliples devices for on user. It's a common practice,
    but not used in this project.
    """

    registration_id = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def send_message(self, title=None, body=None, data=None):
        """Send a push notification with FCM."""
        result = send_fcm_message(
            registration_id=self.registration_id,
            title=title,
            body=body,
            data=data
        )

        if "error" in result["results"][0]:  # TODO : handle deferred
            self.active = False

        return result

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Override the default save method of the model.

        Skip the save if the user and the registration id are already registered together.
        Remove an eventually device already registered with the current user before saving
        the new one.
        Or error if the registration id is already registered with an other user.
        """
        device = self.user.get_device()
        if device is not None:
            if device.registration_id != self.registration_id:
                device.delete()
            else:
                return

        super(Device, self).save(*args, **kwargs)
