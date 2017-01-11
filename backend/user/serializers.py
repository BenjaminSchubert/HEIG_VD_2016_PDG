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
from rest_framework.fields import Field, SerializerMethodField
from rest_framework.serializers import ModelSerializer, CharField, EmailField, ImageField

from user.models import User, Friendship


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class FriendField(Field):
    """
    Field for a friend.

    This will check the `from_account` and `to_account` values and will return the one that is not the current user.

    :param instance_serializer: serializer used to serialize the friend
    :param kwargs: additional arguments to pass to the `Field` constructor
    """

    def __init__(self, instance_serializer, **kwargs):
        """
        Override the default constructor of field to force the `source` to be the whole object.

        This also sets the serializer used internally

        :param kwargs: arguments to pass to the parent constructor
        """
        self.serializer = instance_serializer
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        Transform the current object to its internal representation.

        This also checks that the user is not itself, as we don't accept imaginary friends.

        :param data: id of the friend user
        :raise ValidationError: if the user to be friend with is the current user
        :return: a dictionary with a key `friend` containing the given user
        """
        if data == self.parent.context["request"].user.id:
            raise serializers.ValidationError("Cannot be friend with self.")
        return {"friend": User.objects.get(id=data)}

    def to_representation(self, value):
        """
        Get the friend from the representation, base on the `from_account` and `to_account` of the value given.

        :param value: object to serialize
        :return: the user in the relation that is not the current user
        """
        if self.parent.context["request"].user == value.from_account:
            return self.serializer.to_representation(value.to_account)
        return self.serializer.to_representation(value.from_account)


class BlockedField(Field):
    """
    Field for serializing whether the object is blocked from the current user's point of view.

    This will check the `from_blocking` and `to_blocking` values and
    will return the one that is related to the current user.
    """

    def __init__(self, **kwargs):
        """
        Override the default constructor of field to force the `source` to be the whole object.

        :param kwargs: arguments to pass to the parent constructor
        """
        kwargs['source'] = '*'
        super().__init__(**kwargs)

    def to_internal_value(self, data: bool):
        """
        Get the data correctly formatted.

        :param data: boolean describing whether the current user is blocking the other.
        """
        return {"is_blocked": data}

    def to_representation(self, value):
        """
        Get the correct value for the is_blocked field.

        This will check which of the `from_blocking` and `to_blocking` is related to the current user and return it.

        :param value: object to serialize
        :return: whether the current user is blocking the other or not
        """
        if self.parent.context["request"].user == value.from_account:
            return value.from_blocking
        return value.to_blocking


class HiddenField(Field):
    """
    Field for serializing whether the object is hidden from the current user's point of view.

    This will check the `is_hidden` value and will return it if the current user is the one that
    must accept the request. Otherwise will return False.
    """

    def __init__(self, **kwargs):
        """
        Override the default constructor of field to force the `source` to be the whole object.

        :param kwargs: arguments to pass to the parent constructor
        """
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
        Get the data correctly formatted.

        :param data: boolean describing whether the current user has hidden the request from the other.
        """
        return {"is_hidden": data}

    def to_representation(self, value):
        """
        Get if the request was hidden.

        This will check which of the `is_hidden` and return it if the current user is the one that must accept.
        Otherwise will return `False`

        :param value: object to serialize
        :return: whether the request is hidden or not
        """
        if self.parent.context["request"].user == value.from_account:
            return False  # a user cannot know his request was hidden
        return value.is_hidden


class PhoneNumberSerializerMixin(serializers.Serializer):
    """
    This Serializer adds a phone number and a country fields.

    This allows for the submission of a phone number and its validation under the E.164 format.
    """

    phone_number = CharField(required=False, write_only=True)
    country = CharField(required=False, write_only=True)

    def validate(self, attrs):
        """
        Validate that every attributes of the serializer is valid.

        This mainly checks the phone number.

        :param attrs: attributes to validate
        :return: all valid attributes
        """
        attrs = super().validate(attrs)

        if "phone_number" in attrs and "country" not in attrs:
            raise ValidationError({"country": "This field is required when giving phone number."})
        if "country" in attrs and "phone_number" not in attrs:
            raise ValidationError({"phone_number": "This field is required when giving a country."})

        if "phone_number" in attrs:
            try:
                phone_number = phonenumbers.parse(attrs["phone_number"], attrs["country"])
            except Exception:
                raise ValidationError({"phone_number": "This is not a valid phone number"})
            if not phonenumbers.is_valid_number_for_region(phone_number, attrs["country"]):
                raise ValidationError({"phone_number": "This is not a valid phone number."})

            attrs["phone_number"] = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            attrs.pop("country")

        return attrs


class PublicUserSerializer(ModelSerializer, PhoneNumberSerializerMixin):
    """Defines a serializer for users that only keeps the minimum information."""

    avatar = ImageField(read_only=True)
    email = EmailField(write_only=True)
    password = CharField(max_length=255, write_only=True)

    class Meta:
        """This Meta class defines the fields and models for the `PublicUserSerializer`."""

        fields = ("id", "username", "email", "avatar", "password", "phone_number", "country")
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
            if "unique" in e.args[0].lower():
                error = e.args[0].split(".")[-1].strip()

                if not error:  # PSQL Format
                    error = str(e.args).split("=")[0].split(" ")[-1].replace("(", "").replace(")", "")

                raise ValidationError({error: ["user with this {} already exists".format(error)]})
            raise e


class UserProfileSerializer(ModelSerializer, PhoneNumberSerializerMixin):
    """Defines a serializer for users to edit their profiles."""

    password = CharField(max_length=255, write_only=True, required=False)

    class Meta:
        """This Meta class defines the fields and models for the `UserProfileSerializer`."""

        fields = (
            "id", "username", "email", "avatar", "password", "phone_number", "country", "is_hidden", "is_staff",
        )
        model = User
        read_only_fields = ("id", "avatar")

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
    """Defines a serializer for creating and viewing friend requests."""

    error_message = "You already asked {} as friend"

    friend = FriendField(PublicUserSerializer())
    is_blocked = BlockedField(read_only=True)
    is_hidden = HiddenField(read_only=True)
    initiator = SerializerMethodField()

    class Meta:
        """Defines the fields and models for the `FriendSerializer`."""

        model = Friendship
        fields = ("id", "friend", "initiator", "is_accepted", "is_blocked", "is_hidden")

    def create(self, validated_data):
        """
        Create a new friend request.

        This checks that both users are different and will throw an error otherwise.

        :param validated_data: data to use for friendship creation
        :raise ValidationError: if an integrity violation is done
        :return: the newly created object
        """
        try:
            return super().create(dict(from_account=self.context["request"].user, to_account=validated_data["friend"]))
        except IntegrityError as e:
            if "unique" in e.args[0].lower():
                raise ValidationError({"error": [self.error_message.format(validated_data["friend"].username)]})
            raise e

    def update(self, instance, validated_data):
        """Override the default behavior to raise an exception. We don't want this."""
        raise NotImplementedError("This is not meant to be used")

    def get_initiator(self, obj):
        """Get whether current user is the initiator of the request or not."""
        return obj.from_account == self.context["request"].user


class FriendDetailsSerializer(ModelSerializer):
    """Defines a serializer to view details about a friendship and update it."""

    friend = FriendField(PublicUserSerializer(), read_only=True)
    is_blocked = BlockedField(required=False)
    is_hidden = HiddenField(required=False)
    initiator = SerializerMethodField()

    class Meta:
        """Defines the fields and models for the `FriendDetailsSerializer`."""

        model = Friendship
        fields = ("friend", "initiator", "is_accepted", "is_blocked", "is_hidden")

    def create(self, validated_data):
        """Override the default behavior to raise an exception. We don't want this."""
        raise NotImplementedError("This is not meant to be used")

    def update(self, instance, validated_data):
        """
        Update the given instance with the new data.

        This will reassign fields based on whether the user is the initiator or receiver of the request.

        :param instance: friendship instance to update
        :param validated_data: data to use for update
        :return: the update instance
        """
        blocked = validated_data.pop("is_blocked", None)
        if blocked is not None:
            if self.context["request"].user == instance.from_account:
                validated_data["from_blocking"] = blocked
            else:
                validated_data["to_blocking"] = blocked

        return super().update(instance, validated_data)

    def validate(self, attrs):
        """
        Validate that the given attributes do not violate the workflow of a friendship request.

        :param attrs: attributes to check
        :raise ValidationError: if there is an error with one attribute
        :return: the attributes once checked
        """
        if self.instance.to_account != self.context["request"].user:
            if attrs.get("is_accepted", False):
                raise ValidationError("You have to be the user to which the friendship request is sent to accept it.")
            elif attrs.get("is_hidden", False):
                raise ValidationError("You have to be the user to which the friendship request is sent to hide it.")

        if attrs.get("is_blocked", False) and not self.instance.is_accepted:
            raise ValidationError("You cannot block a friend when the request was not accepted.")
        elif attrs.get("is_hidden", False) and self.instance.is_accepted:
            raise ValidationError("You cannot hide a request that was accepted.")
        elif not attrs.get("is_accepted", True) and self.instance.is_accepted:
            raise ValidationError("You cannot un-accept a request that was accepted.")

        return attrs

    def get_initiator(self, obj):
        """Get whether current user is the initiator of the request or not."""
        return obj.from_account == self.context["request"].user
