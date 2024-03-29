"""Contains all models from the `meeting` module."""

from django.db import models
from django.conf import settings
from popo_attribute_tracker.attribute_tracker import AttributeTrackerMixin

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class Place(models.Model):
    """Extends `Model` to define places to which meetings can be done."""

    # 6 decimals allows for approximately a 10 cm precision, which is below non-military GPS precision
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    name = models.CharField(max_length=255, null=True)


class Meeting(models.Model, AttributeTrackerMixin):
    """Extends `Model` to define meetings."""

    STATUS_PENDING = "pending"
    STATUS_PROGRESS = "progress"
    STATUS_ENDED = "ended"
    STATUS_CANCELED = "canceled"

    TYPE_PLACE = "place"
    TYPE_PERSON = "person"
    TYPE_SHORTEST = "shortest"

    start_time = models.DateTimeField(auto_now_add=True)
    meeting_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    type = models.CharField(
        choices=((TYPE_PLACE, TYPE_PLACE), (TYPE_PERSON, TYPE_PERSON), (TYPE_SHORTEST, TYPE_SHORTEST)),
        max_length=8
    )
    status = models.CharField(
        choices=(
            (STATUS_PENDING, STATUS_PENDING),
            (STATUS_PROGRESS, STATUS_PROGRESS),
            (STATUS_ENDED, STATUS_ENDED),
            (STATUS_CANCELED, STATUS_CANCELED)
        ),
        max_length=8,
        default=STATUS_PENDING
    )

    organiser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="organizing")
    on = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None, related_name="meeting_point_for")

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Participant")

    TRACKED_ATTRS = ("status",)


class Participant(models.Model, AttributeTrackerMixin):
    """
    Extends `Model` to define participants to meetings.

    The participants can accept or refuse a meeting and must signal once they are arrived.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    meeting = models.ForeignKey(Meeting)

    accepted = models.NullBooleanField(default=None)
    arrived = models.BooleanField(default=False)
    place = models.ForeignKey(Place, null=True, max_length=255)

    TRACKED_ATTRS = ("accepted", "arrived")

    class Meta:
        """Metaclass for the `Participant` model."""

        unique_together = ("user", "meeting")
