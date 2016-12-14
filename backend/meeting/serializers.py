from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer

from meeting.models import Meeting, Place, Participant


class PlaceSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Place

    def get_attribute(self, instance):
        return Participant.objects.get(user=self.context["request"].user, meeting=instance).place


class MeetingSerializer(ModelSerializer):
    place = PlaceSerializer(required=False)

    class Meta:
        fields = "__all__"
        model = Meeting
        extra_kwargs = {
            "organiser": dict(read_only=True, default=CurrentUserDefault()),
            "participants": dict(required=True, read_only=False, queryset=get_user_model().objects.all()),
        }

    @transaction.atomic
    def create(self, validated_data):
        participants = validated_data.pop("participants")
        place = validated_data.pop("place", None)

        meeting = super().create(validated_data)
        place = Place(**place)
        place.save()

        for participant in participants:
            Participant(user=participant, place=place, meeting=meeting).save()

        return meeting

    def validate(self, attrs):
        attrs = super().validate(attrs)
        errors = dict()

        if self.context["request"].user not in attrs["participants"]:
            attrs["participants"].append(self.context["request"].user)

        if len(attrs["participants"]) < 2:
            errors["participants"] = "You need at least one participant in addition of yourself to create a meeting"

        if len(errors):
            raise ValidationError(errors)

        return attrs
