"""This module defines all the serializers for the `meeting` application."""

from itertools import chain

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, HiddenField, DecimalField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, Serializer

from meeting.models import Meeting, Place, Participant
from user.models import Friendship
from user.serializers import PublicUserSerializer

__author__ = "Benjamin Schubert, <ben.c.schubert@gmail.com>"


class AutoShrinkDecimal(DecimalField):
    """Extend `DecimalField` to automatically strip to the number of decimal given."""

    def validate_precision(self, value):
        """Round the value to 6 numbers before sending to the parent for further validation."""
        return super().validate_precision(Decimal(round(value, self.decimal_places)))


class PlaceSerializer(ModelSerializer):
    """Defines a serializer for the `Place` model for editing."""

    latitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=90, min_value=-90)
    longitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=180, min_value=-180)

    class Meta:
        """Defines the metaclass for the `PlaceSerializer`."""

        fields = "__all__"
        model = Place


class MeetingPlaceSerializer(ModelSerializer):
    """
    Defines a serializer for the `Place` model when used in a `Meeting`.

    This will use the correct place for the user, allowing users to give different names to places, independently of
    each others.
    """

    latitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=90, min_value=-90)
    longitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=180, min_value=-180)

    class Meta:
        """Defines the metaclass for the `MeetingPlaceSerializer`."""

        fields = "__all__"
        model = Place

    def get_attribute(self, instance):
        """
        Get the correct place for the requesting user.

        :param instance: meeting for which to get the place
        :return: a `Place` instance
        """
        return Participant.objects.get(user=self.context["request"].user, meeting=instance).place


class ParticipantSerializer(ModelSerializer):
    """
    Defines a serializer for `Participant` in a meeting.

    This will not give information that are redundant with the `MeetingSerializer`.
    """

    user = PublicUserSerializer(read_only=True)

    class Meta:
        """Defines the metaclass for the `ParticipantSerializer`."""

        exclude = ("place", "id", "meeting")
        model = Participant
        read_only_fields = ("user",)

    def validate(self, attrs):
        """
        Check that the data is valid for the update of a participant.

        :param attrs: attributes to check
        :exception ValidationError: when any of the attribute is invalid
        :return: sanitized version of the attributes
        """
        attrs = super().validate(attrs)

        if self.instance.meeting.status == Meeting.STATUS_ENDED:
            raise ValidationError("This meeting is finished.")
        elif self.instance.meeting.status == Meeting.STATUS_CANCELED:
            raise ValidationError("This meeting is canceled.")
        elif self.instance.accepted is False:
            raise ValidationError("You already refused this meeting.")

        if "arrived" in attrs:
            if attrs["arrived"] is True and self.instance.accepted is not True:
                raise ValidationError({"accepted": "You have not accepted this meeting."})
            elif attrs["arrived"] is False:
                raise ValidationError({"accepted": "Operation not permitted."})

        return attrs


class MeetingSerializer(ModelSerializer):
    """
    Defines a serializer for `Meeting` objects.

    This is essentially a serializer for read representation of meetings. For easier creation or update, please see
    the `WriteMeetingSerializer` which is optimized for write operations.
    """

    organiser = PublicUserSerializer(read_only=True)
    place = MeetingPlaceSerializer(required=False)
    participants = ParticipantSerializer(many=True, source="participant_set")

    class Meta:
        """Defines the metaclass for the `MeetingSerializer`."""

        exclude = ("end_time", "start_time")
        model = Meeting
        depth = 1


class WriteMeetingSerializer(MeetingSerializer):
    """
    Defines a serializer for `Meeting` objects.

    This is a write-optimized version of the `MeetingSerializer`.
    """

    organiser = HiddenField(default=CurrentUserDefault())
    participants = PrimaryKeyRelatedField(
        required=True, read_only=False, queryset=get_user_model().objects.all(), many=True
    )

    class Meta(MeetingSerializer.Meta):
        """Metaclass for the `WriteMeetingSerializer`."""

        exclude = ("status",)
        depth = 0

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new meeting.

        This operation is atomic and will create every participant and places accordingly.

        If this is a 'place' meeting, set the status as 'in progress'. Other types of meetings
        needs more information to start.

        For 'hidden' user, automatically refuse all meetings.

        :param validated_data: data to use for the creation of the meeting
        :return: the newly created meeting
        """
        participants = validated_data.pop("participants")
        place = validated_data.pop("place", None)
        current_user = self.context["request"].user

        if "type" in validated_data and validated_data["type"] == Meeting.TYPE_PLACE:
            validated_data["status"] = Meeting.STATUS_PROGRESS

        meeting = super().create(validated_data)

        if place is not None:
            place = Place(**place)
            place.save()

        for participant in participants:
            accepted = None
            if participant.is_hidden is True:
                accepted = False
            elif current_user.id == participant.id:
                accepted = True

            Participant(
                user=participant,
                place=place,
                meeting=meeting,
                accepted=accepted
            ).save()

        return meeting

    def validate(self, attrs):
        """
        Check that the data is valid for the creation of a meeting.

        :param attrs: attributes to check
        :exception ValidationError: when any of the attribute is invalid
        :return: sanitized version of the attributes
        """
        current_user = self.context["request"].user
        attrs = super().validate(attrs)
        errors = dict()

        if attrs["type"] == "place" and attrs.get("place", None) is None:
            errors["place"] = "This field is required when having 'place' as 'type',."

        if self.context["request"].user not in attrs["participants"]:
            attrs["participants"].append(current_user)

        if len(attrs["participants"]) < 2:
            errors["participants"] = "You need at least one participant in addition of yourself to create a meeting"

        participants = set(participant.id for participant in attrs["participants"])

        friends = chain.from_iterable(Friendship.objects.filter(
            Q(from_account=current_user, is_accepted=True, from_blocking=False, to_account__is_active=True) |
            Q(to_account=current_user, is_accepted=True, to_blocking=False, from_account__is_active=True)
        ).values_list("from_account", "to_account"))

        not_friends = participants - set(friends) - {current_user.id}

        if len(not_friends):
            errors["participants"] = "The following users are not friends with you : {}".format(
                ",".join(map(str, not_friends))
            )

        if len(errors):
            raise ValidationError(errors)

        return attrs


class MeetingUpdateSerializer(ModelSerializer):
    """Defines a serializer for the `Meeting` model for editing."""

    class Meta:
        """Defines the metaclass for the `MeetingUpdateSerializer`."""

        fields = ("status",)
        model = Meeting

    def validate(self, attrs):
        """
        Check that the data is valid for the update of a meeting.

        :param attrs: attributes to check
        :exception ValidationError: when any of the attribute is invalid
        :return: sanitized version of the attributes
        """
        attrs = super().validate(attrs)

        if self.instance.status == Meeting.STATUS_ENDED:
            raise ValidationError("You cannot update an finished meeting.")
        elif self.instance.status == Meeting.STATUS_CANCELED:
            raise ValidationError("You cannot update an canceled meeting.")

        if "status" in attrs and attrs["status"] == Meeting.STATUS_PENDING:
            raise ValidationError({"status": "You cannot pause a running meeting."})

        return attrs


class PositionSerializer(Serializer):
    """
    Defines a serializer for devices that only allow to write the device registration id.

    Automatically attach the current logged in user to the added device.
    """

    latitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=90, min_value=-90)
    longitude = AutoShrinkDecimal(decimal_places=6, max_digits=9, max_value=180, min_value=-180)
