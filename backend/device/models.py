"""Contains all models from the `device` module."""

from django.db import models
from django.conf import settings

from device.fcm import send_fcm_bulk_message, send_fcm_message

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeviceManager(models.Manager):
    """Overrides the default Manager with our custom one."""

    def get_queryset(self):
        """Provide a custom QuerySet for devices."""
        return DeviceQuerySet(self.model)


class DeviceQuerySet(models.query.QuerySet):
    """
    Overrides the default QuerySet with our custom one.

    Provide a function to send a message to a QuerySet (a selection of devices).
    """

    def send_message(self, title=None, body=None, type=None, deferred=True):
        """
        Send a push message to the devices, allowing the message to be deferred if sending failed.

        Will mark the device as inactive if sending fails
        and won't try to send a message to an already inactive device.

        :param title: the title of the message
        :param body: the body of the message
        :param type: the type of the message
        :param deferred: define if message can be deferred or not
        """
        if deferred is True:
            for device in self.filter(is_active=False):
                DeferredMessage(user_id=device.user_id, title=title, body=body, type=type).save()

        devices = list(self.filter(is_active=True).all())
        result = send_fcm_bulk_message(
            registration_ids=[d.registration_id for d in devices],
            title=title,
            body=body,
            data=dict(type=type)
        )

        for (index, result) in enumerate(result[0]["results"]):
            if "error" in result:
                self.filter(id=devices[index].id).update(is_active=False)

                if deferred is True:
                    DeferredMessage(user_id=devices[index].user_id, title=title, body=body, type=type).save()


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

    objects = DeviceManager()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Override save method to delete eventually existing device attached to the user."""
        Device.objects.filter(user_id=self.user_id).delete()
        super(Device, self).save(force_insert, force_update, using, update_fields)

    def send_message(self, title=None, body=None, type=None, deferred=True):
        """
        Send a push message to the device, allowing the message to be deferred if sending failed.

        Will mark the device as inactive if sending fails
        and won't try to send a message to an already inactive device.

        :param title: the title of the message
        :param body: the body of the message
        :param type: the type of the message
        :param deferred: define if message can be deferred or not
        :return: True if the message was successfully sent, False otherwise.
        """
        if self.is_active is False:
            if deferred is True:
                DeferredMessage(user_id=self.user_id, title=title, body=body, type=type).save()
            return False

        else:
            result = send_fcm_message(
                registration_id=self.registration_id,
                title=title,
                body=body,
                data=dict(type=type)
            )
            if result["success"] == 0:
                Device.objects.filter(id=self.id).update(is_active=False)

                if deferred is True:
                    DeferredMessage(user_id=self.user_id, title=title, body=body, type=type).save()
                return False

            return True

    def send_deferred_message(self, message):
        """
        Try to send again the message to the specified device.

        If the message was successful sent, remove it from the database.

        :return: True if the message was successfully sent, False otherwise.
        """
        if self.send_message(message.title, message.body, message.type, False) is True:
            message.delete()
            return True
        return False


class DeferredMessage(models.Model):
    """Extends `Model` to keep information about messages which could not be sent."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.TextField(null=True)
    body = models.TextField(null=True)
    type = models.TextField(null=True)
