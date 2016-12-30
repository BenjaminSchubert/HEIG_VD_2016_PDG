"""Contains all models from the `device` module."""

from django.db import models
from django.conf import settings

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class Device(models.Model):
    """
    Extends `Model` to keep information about devices.

    Device has a One to One relation. The foreign key is located on the device
    to allow eventually multiples devices for on user. It's a common practice,
    but not used in this project.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    registration_id = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Override save method to delete eventually existing device attached to the user."""
        Device.objects.filter(user=self.user).delete()
        super(Device, self).save(force_insert, force_update, using, update_fields)


class DeferredMessage(models.Model):
    """Extends `Model` to keep information about messages which could not be sent."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.TextField(null=True)
    body = models.TextField(null=True)
    type = models.TextField(null=True)
    last_try = models.DateTimeField(auto_now=True)

    def send(self):
        """
        Try to send again the message to the user.

        If the message was successful sent, remove it from the database.

        :return: True if the message was successfully sent, False otherwise.
        """
        if self.user.send_message(title=self.title, body=self.body, type=self.type, deferred=False) is True:
            self.delete()
            return True
        else:
            self.last_try.now()
            self.save(update_fields=["last_try"])
            return False
