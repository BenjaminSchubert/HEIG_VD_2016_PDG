"""This module defines all the serializers for the `user` application."""


from io import BytesIO

import phonenumbers
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer, CharField, EmailField, ImageField

from user.models import User, Friendship


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


class FriendField(Field):
    def __init__(self, instance_serializer, **kwargs):
        self.serializer = instance_serializer
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data == self.parent.context["request"].user.id:
            raise serializers.ValidationError("Cannot be friend with self.")
        return {"friend": User.objects.get(id=data)}

    def to_representation(self, value):
        if self.parent.context["request"].user == value.from_account:
            return self.serializer.to_representation(value.to_account)
        return self.serializer.to_representation(value.from_account)


class BlockedField(Field):
    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return {"is_blocked": data}

    def to_representation(self, value):
        if self.parent.context["request"].user == value.from_account:
            return value.from_blocking
        return value.to_blocking


class HiddenField(Field):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return {"is_hidden": data}

    def to_representation(self, value):
        if self.parent.context["request"].user == value.from_account:
            return False  # a user cannot know his request was hidden
        return value.is_hidden


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
        avatar = validated_data["avatar"]
        image = Image.open(avatar)
        image.thumbnail(settings.THUMBNAILS_SIZE, Image.ANTIALIAS)

        temp_data = BytesIO()
        image.save(temp_data, "PNG")

        avatar.close()
        validated_data["avatar"] = InMemoryUploadedFile(
            temp_data, None, "{}.png".format(instance.id), "image/png", len(temp_data.getvalue()), None
        )

        instance.last_avatar_update = timezone.now()
        return super().update(instance, validated_data)


class FriendSerializer(ModelSerializer):
    error_message = "You already asked {} as friend"

    friend = FriendField(PublicUserSerializer())
    is_blocked = BlockedField(read_only=True)
    is_hidden = HiddenField(read_only=True)

    class Meta:
        model = Friendship
        fields = ("friend", "is_accepted", "is_blocked", "is_hidden")

    def create(self, validated_data):
        try:
            return super().create(dict(from_account=self.context["request"].user, to_account=validated_data["friend"]))
        except IntegrityError as e:
            if "UNIQUE" in e.args[0]:
                raise ValidationError({"error": [self.error_message.format(validated_data["friend"].username)]})
            raise e

    def update(self, instance, validated_data):
        raise NotImplementedError("This is not meant to be used")


class FriendDetailsSerializer(ModelSerializer):
    friend = FriendField(PublicUserSerializer(), read_only=True)
    is_blocked = BlockedField(required=False)
    is_hidden = HiddenField(required=False)

    class Meta:
        model = Friendship
        fields = ("friend", "is_accepted", "is_blocked", "is_hidden")

    def create(self, validated_data):
        raise NotImplementedError("This is not meant to be used")

    def update(self, instance, validated_data):
        blocked = validated_data.pop("is_blocked", None)
        if blocked is not None:
            if self.context["request"].user == instance.from_account:
                validated_data["from_blocking"] = blocked
            else:
                validated_data["to_blocking"] = blocked

        return super().update(instance, validated_data)

    def validate(self, attrs):
        if self.instance.to_account != self.context["request"].user:
            if attrs.get("is_accepted", False):
                raise ValidationError("You have to be the user to which the friendship request is sent to accept it.")
            elif attrs.get("is_hidden", False):
                raise ValidationError("You have to be the user to which the friendship request is sent to hide it.")

        if attrs.get("is_blocked", False) and not self.instance.is_accepted:
            raise ValidationError("You cannot block a friend when the request was not accepted.")
        elif attrs.get("is_hidden", False) and self.instance.is_accepted:
            raise ValidationError("You cannot hide a request that was accepted")

        return attrs
