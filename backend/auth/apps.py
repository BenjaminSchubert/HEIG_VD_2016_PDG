"""Declares and configures the `auth` application."""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """`auth` application configuration."""

    name = 'auth'
    label = 'rady.auth'
