"""This module defines all the serializers for the `user` application."""


import os

import phonenumbers
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, CharField, EmailField, ImageField

from user.models import User


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


def validate_phone_number(value: str):
    """
    Validate that the given value is a valid phone number.

    :param value: value to check
    :raise ValidationError: when the phone number is not valid
    """
    if not phonenumbers.is_possible_number_string(value, None):
        raise serializers.ValidationError(
            "{} is not a possible phone number under the E.164 specification".format(value)
        )


class PublicUserSerializer(ModelSerializer):
    """Defines a serializer for users that only keeps the minimum information."""

    avatar = ImageField(read_only=True)
    email = EmailField(write_only=True)
    password = CharField(max_length=255, write_only=True)

    class Meta:
        """This Meta class defines the fields and models for the `PublicUserSerializer`."""

        fields = ("username", "email", "avatar", "password")
        model = User

    def create(self, validated_data):
        """
        Create a new user.

        :param validated_data: data to use for the creation of the user
        :return: the new user instance
        """
        try:
            return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            error = e.args[0].split(".")[-1]
            if "UNIQUE" in e.args[0]:
                raise ValidationError({error: ["user with this {} already exists".format(error)]})
            raise e


class UserProfileSerializer(ModelSerializer):
    """Defines a serializer for users to edit their profiles."""

    password = CharField(max_length=255, write_only=True, required=False)
    avatar = ImageField(read_only=True)
    phone_number = CharField(required=False, validators=[validate_phone_number])

    class Meta:
        """This Meta class defines the fields and models for the `UserProfileSerializer`."""

        fields = ("username", "email", "avatar", "password", "phone_number", "last_avatar_update")
        model = User

    def update(self, instance, validated_data):
        """
        Update the given instance with new validated_data.

        :param instance: instance to update
        :param validated_data: data to use for update
        :return: the newly updated data
        """
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
            validated_data.pop("password")

        if "phone_number" in validated_data:
            instance.set_phone_number(validated_data["phone_number"])
            validated_data.pop("phone_number")

        return super().update(instance, validated_data)


class UserAvatarSerializer(ModelSerializer):
    """Defines a serializer to allow a user to update its avatar."""

    class Meta:
        """This Meta class defines the fields and models for the `UserAvatarSerializer`."""

        fields = ("avatar",)
        model = User

    def update(self, instance, validated_data):
        """
        Update the user's avatar.

        :param instance: user to update
        :param validated_data: data containing the file to use as new avatar
        :return: the new updated instance of the user
        """
        extension = os.path.splitext(validated_data["avatar"].name)[1]
        validated_data["avatar"].name = "{}{}".format(instance.id, extension)
        instance.last_avatar_update = timezone.now()
        return super().update(instance, validated_data)
