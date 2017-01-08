"""This module defines all the serializers for the `device` application."""

from rest_framework.fields import HiddenField, CurrentUserDefault
from rest_framework.serializers import ModelSerializer

from device.models import Device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeviceSerializer(ModelSerializer):
    """
    Defines a serializer for devices that only allow to write the device registration id.

    Automatically attach the current logged in user to the added device.
    """

    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        """Defines the metaclass for the `DeviceSerializer`."""

        model = Device
        fields = ("registration_id", "user")
        write_only_fields = ("registration_id",)
