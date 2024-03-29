"""Contains all models from the `device` module."""

from django.db import models
from django.conf import settings
from jsonfield import JSONField

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

    def send_message(self, title=None, body=None, data=None, deferred=True, related_type=None, related_id=None):
        """
        Send a push message to the devices, allowing the message to be deferred if sending failed.

        Will mark the device as inactive if sending fails
        and won't try to send a message to an already inactive device.

        :param title: the title of the message
        :param body: the body of the message
        :param data: a Json object attached to the message
        :param deferred: define if message can be deferred or not
        :param related_type: define a type of object to which the message is attached
        :param related_id: define an id of object to which the message is attached
        """
        if deferred is True:
            for device in self.filter(is_active=False):
                DeferredMessage(
                    user_id=device.user_id,
                    title=title,
                    body=body,
                    data=data,
                    related_type=related_type,
                    related_id=related_id,
                ).save()

        devices = list(self.filter(is_active=True).all())
        if devices:
            result = send_fcm_bulk_message(
                registration_ids=[d.registration_id for d in devices],
                title=title,
                body=body,
                data=data
            )

            for (index, result) in enumerate(result[0]["results"]):
                if "error" in result:
                    self.filter(id=devices[index].id).update(is_active=False)

                    if deferred is True:
                        DeferredMessage(
                            user_id=devices[index].user_id,
                            title=title,
                            body=body,
                            data=data,
                            related_type=related_type,
                            related_id=related_id,
                        ).save()


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

    def send_message(self, title=None, body=None, data=None, deferred=True, related_type=None, related_id=None):
        """
        Send a push message to the device, allowing the message to be deferred if sending failed.

        Will mark the device as inactive if sending fails
        and won't try to send a message to an already inactive device.

        :param title: the title of the message
        :param body: the body of the message
        :param data: a Json object attached to the message
        :param deferred: define if message can be deferred or not
        :param related_type: define a type of object to which the message is attached
        :param related_id: define an id of object to which the message is attached
        :return: True if the message was successfully sent, False otherwise.
        """
        if self.is_active is False:
            if deferred is True:
                DeferredMessage(
                    user_id=self.user_id,
                    title=title,
                    body=body,
                    data=data,
                    related_type=related_type,
                    related_id=related_id,
                ).save()
            return False

        else:
            result = send_fcm_message(
                registration_id=self.registration_id,
                title=title,
                body=body,
                data=data
            )
            if result["success"] == 0:
                Device.objects.filter(id=self.id).update(is_active=False)

                if deferred is True:
                    DeferredMessage(
                        user_id=self.user_id,
                        title=title,
                        body=body,
                        data=data,
                        related_type=related_type,
                        related_id=related_id,
                    ).save()
                return False

            return True

    def send_deferred_message(self, message):
        """
        Try to send again the message to the specified device.

        If the message was successful sent, remove it from the database.

        :return: True if the message was successfully sent, False otherwise.
        """
        if self.send_message(message.title, message.body, message.data, False) is True:
            message.delete()
            return True
        return False


class DeferredMessage(models.Model):
    """Extends `Model` to keep information about messages which could not be sent."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.TextField(null=True)
    body = models.TextField(null=True)
    data = JSONField(null=True)
    related_type = models.CharField(max_length=16, null=True)
    related_id = models.PositiveIntegerField(null=True)
