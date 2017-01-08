"""Contains all signal handlers from the `meeting` module."""
from django.db.models import Q
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from device.models import DeferredMessage
from meeting.models import Participant, Meeting

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(post_init, sender=Participant)
def post_init_participant(instance, **kwargs):
    """
    Fired when instantiate a participant object model, signal sent at the end of the model init method.

    It initialize the attribute tracker for the Participant model.
    """
    instance.initialize_tracker()


@receiver(post_save, sender=Participant)
def post_save_participant(instance, created, **kwargs):
    """
    Fired when participant is saved (created or updated).

    Creation :
    - Send a push notification to the user to inform him of the new meeting (prevent to inform
      the organiser of is own meeting).
    Update :
    - Send a push notification to the other users to inform them of the event (no push message to
      the person at the origin of the action and the participants who declined the meeting).
    """
    if created:
        if instance.meeting.organiser_id != instance.user_id:
            instance.user.send_message(
                title="New meeting",
                body="{} added you to a meeting".format(instance.meeting.organiser.username),
                data=dict(type="new-meeting", meeting=instance.meeting.id),
                related_type="meeting",
                related_id=instance.meeting.id,
            )

    else:
        if instance.has_changed("accepted"):
            meeting_users = instance.meeting.participants \
                .exclude(Q(id=instance.user.id) | Q(participant__accepted=False)) \
                .all()

            if instance.accepted is True:
                meeting_users.send_message(
                    title="Meeting update",
                    body="{} accepted the meeting".format(instance.user.username),
                    data=dict(type="user-accepted-meeting", meeting=instance.meeting.id, participant=instance.id),
                    deferred=False,
                )

            elif instance.accepted is False:
                meeting_users.send_message(
                    title="Meeting update",
                    body="{} refused the meeting".format(instance.user.username),
                    data=dict(type="user-refused-meeting", meeting=instance.meeting.id, participant=instance.id),
                    deferred=False,
                )

        elif instance.has_changed("arrived") and instance.arrived is True:
            meeting_users = instance.meeting.participants \
                .exclude(id=instance.user.id) \
                .filter(participant__accepted=True) \
                .all()

            meeting_users.send_message(
                title="Meeting update",
                body="{} has arrived to the meeting".format(instance.user.username),
                data=dict(type="user-arrived-to-meeting", meeting=instance.meeting.id, participant=instance.id),
                deferred=False,
            )
    instance.reset_tracker()


@receiver(post_init, sender=Meeting)
def post_init_meeting(instance, **kwargs):
    """
    Fired when instantiate a meeting object model, signal sent at the end of the model init method.

    It initialize the attribute tracker for the Meeting model.
    """
    instance.initialize_tracker()


@receiver(post_save, sender=Meeting)
def post_save_meeting(instance, created, **kwargs):
    """
    Fired when meeting is saved (created or updated).

    Update :
    - If the status is now 'progress'
        - Send a push message to inform the participants.
    - If the status is now 'ended'
        - Send a push message to inform the participants.
        - Remove eventually pending push messages related to the meeting.
    """
    if created is False:
        if instance.has_changed("status"):
            meeting_users = instance.participants\
                .filter(participant__accepted=True)\
                .all()

            if instance.status == Meeting.STATUS_PROGRESS:
                meeting_users.send_message(
                    title="Meeting in progress",
                    body="Go to the meeting now",
                    data=dict(type="meeting-in-progress", meeting=instance.id),
                    deferred=False,
                )

            elif instance.status == Meeting.STATUS_ENDED:
                meeting_users.send_message(
                    title="Meeting finished",
                    body="The meeting is now finished",
                    data=dict(type="finished-meeting", meeting=instance.id),
                    deferred=False,
                )
                DeferredMessage.objects.filter(related_type="meeting", related_id=instance.id).delete()

            elif instance.status == Meeting.STATUS_CANCELED:
                meeting_users.send_message(
                    title="Meeting canceled",
                    body="The meeting has been canceled",
                    data=dict(type="canceled-meeting", meeting=instance.id),
                    deferred=False,
                )
                DeferredMessage.objects.filter(related_type="meeting", related_id=instance.id).delete()
    instance.reset_tracker()
