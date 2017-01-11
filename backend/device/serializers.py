"""This module defines all the serializers for the `device` application."""

from rest_framework.serializers import ModelSerializer

from device.models import Device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeviceSerializer(ModelSerializer):
    """Defines a serializer for devices that only allow to write the device registration id."""

    class Meta:
        """Defines the metaclass for the `DeviceSerializer`."""

        model = Device
        fields = ("registration_id",)
        write_only_fields = ("registration_id",)
