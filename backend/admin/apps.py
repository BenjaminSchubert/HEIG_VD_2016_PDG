"""Declares and configures the `admin` application."""

from django.apps import AppConfig


class AdminConfig(AppConfig):
    """Defines the default configuration for the `admin` application."""

    name = 'admin'
    label = 'rady.admin'
