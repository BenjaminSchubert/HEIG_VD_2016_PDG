from django.db import models
from django.conf import settings


class Place(models.Model):
    # 6 decimals allows for approximately a 10 cm precision, which is below non-military GPS precision
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    name = models.CharField(max_length=255, null=True)


class Meeting(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    meeting_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    type = models.CharField(
        choices=(("place", "place",), ("person", "person",), ("shortest", "shortest",)),
        max_length=16
    )

    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="organizing")
    on = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None, related_name="meeting_point_for")

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Participant")


class Participant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    meeting = models.ForeignKey(Meeting)

    accepted = models.NullBooleanField(default=None)
    arrived = models.BooleanField(default=False)
    place = models.ForeignKey(Place, null=True, max_length=255)

    class Meta:
        unique_together = ("user", "meeting")
