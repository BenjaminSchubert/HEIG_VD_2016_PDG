"""This module defines all the serializers for the `admin` application."""

from rest_framework.serializers import ModelSerializer

from user.models import User


__author__ = "Benjamin Schubert <ben.c.schhubert@gmail.com>"


class UserSerializer(ModelSerializer):
    """Defines a serializer for the `User` model to allow administrators to handle their rights."""

    class Meta:
        """Metaclass for the UserSerializer."""

        model = User
        fields = ("id", "is_active", "is_staff", "username", "email",)
        read_only_fields = ("id", "username", "email")
