"""This module defines all the serializers for the `user` application."""


from django.utils import timezone
from rest_framework.serializers import ModelSerializer, CharField, EmailField, ImageField
from rest_framework.validators import UniqueValidator

from user.models import User


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class PublicUserSerializer(ModelSerializer):
    """Defines a serializer for users that only keeps the minimum information."""

    avatar = ImageField(read_only=True)
    email = EmailField(write_only=True, validators=[UniqueValidator(User.objects.all())])
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
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(ModelSerializer):
    """Defines a serializer for users to edit their profiles."""

    password = CharField(max_length=255, write_only=True, required=False)
    # FIXME : this validation should not be done, and the database should catch this
    email = EmailField(validators=[UniqueValidator(User.objects.all())])
    avatar = ImageField(read_only=True)

    class Meta:
        """This Meta class defines the fields and models for the `UserProfileSerializer`."""

        fields = ("username", "email", "avatar", "password", "phone_number")
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
        instance.last_avatar_update = timezone.now()
        return super().update(instance, validated_data)
