"""Declares and configures the `meeting` application."""


from django.apps import AppConfig


class MeetingConfig(AppConfig):
    """Defines the default configuration for the `meeting` application."""

    name = 'meeting'

    def ready(self):
        """Initialization tasks."""
        import meeting.signals  # noqa
