"""Declares and configures the `stats` application."""

from django.apps import AppConfig


class StatsConfig(AppConfig):
    """Defines the configuration for the `stats` application."""

    name = 'stats'

    def ready(self):
        """Initialization tasks."""
        import stats.signals  # noqa
