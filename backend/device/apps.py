"""Declares and configures the `device` application."""

from django.apps import AppConfig


class DeviceConfig(AppConfig):
    """Defines the configuration for the `device` application."""

    name = "device"

    def ready(self):
        """Initialization tasks."""
        import device.signals  # noqa
