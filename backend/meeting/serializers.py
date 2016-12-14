from itertools import chain

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, HiddenField, IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from meeting.models import Meeting, Place, Participant
from user.models import Friendship


class PlaceSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Place

    def get_attribute(self, instance):
        return Participant.objects.get(user=self.context["request"].user, meeting=instance).place


class ParticipantSerializer(ModelSerializer):
    class Meta:
        exclude = ("place", "id", "meeting")
        model = Participant


class MeetingSerializer(ModelSerializer):
    organiser = IntegerField(source="organiser.id")
    place = PlaceSerializer(required=False)
    participants = ParticipantSerializer(many=True, source="participant_set")

    class Meta:
        fields = "__all__"
        model = Meeting
        depth = 1


class WriteMeetingSerializer(MeetingSerializer):
    organiser = HiddenField(default=CurrentUserDefault())
    participants = PrimaryKeyRelatedField(
        required=True, read_only=False, queryset=get_user_model().objects.all(), many=True
    )

    class Meta(MeetingSerializer.Meta):
        depth = 0

    @transaction.atomic
    def create(self, validated_data):
        participants = validated_data.pop("participants")
        place = validated_data.pop("place", None)

        meeting = super().create(validated_data)

        if place is not None:
            place = Place(**place)
            place.save()

        for participant in participants:
            Participant(user=participant, place=place, meeting=meeting).save()

        return meeting

    def validate(self, attrs):
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
            errors["participants"] = "The following users are not friends with you : {}".format(",".join(map(str, not_friends)))

        if len(errors):
            raise ValidationError(errors)

        return attrs

