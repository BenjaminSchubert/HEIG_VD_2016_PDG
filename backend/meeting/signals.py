"""Contains all signal handlers from the `meeting` module."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from meeting.models import Participant

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(post_save, sender=Participant)
def post_save_meeting(instance, created, **kwargs):
    """
    Fired when participant is saved (created or updated).

    Creation :
    - Send a push notification to the user to inform him of the new meeting.
    """
    if created:
        device = instance.user.get_device()
        if device is not None:
            device.send_message(
                title="New gathering",
                body="{} added you to a meeting".format(instance.meeting.organiser.username),
                type="new-gathering",
            )
