"""Declares and configures the `user` application."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Defines the configuration for the `user` application."""

    name = 'user'

    def ready(self):
        """Initialization tasks."""
        import user.signals  # noqa
