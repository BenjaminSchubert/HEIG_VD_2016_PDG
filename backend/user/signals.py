"""Contains all signal handlers from the `users` module."""

from django.db.models.signals import post_init, pre_save, post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(pre_save, sender=FCMDevice)
def pre_save_device(instance, **kwargs):
    """
    Fired when a new device is created.

    It remove eventual devices already attached to the current logged in user.
    """
    FCMDevice.objects.filter(user_id=instance.user_id).delete()


@receiver(post_save, sender=Friendship)
def reset_tracker(instance, **kwargs):
    instance.initialize_tracker()


@receiver(post_save, sender=Friendship)
def post_save_friendship(instance, created, **kwargs):
    """
    Fired when friendship relation is saved (created or updated).

    Creation :
    - Send a push notification to the user who need to accept/refuse the request.
    Update :
    - Send a push notification to the user who asked for the friendship that the relation has been accepted.
    """
    if created:
        device = instance.to_account.get_device()
        if device is not None:
            device.send_message(
                title="New friend request",
                body="{} wants to be your friend".format(instance.from_account.username),
                data={"type": "friend-request"}
            )
    elif instance.has_changed("is_accepted") and instance.is_accepted is True:
        device = instance.from_account.get_device()
        if device is not None:
            device.send_message(
                title="Friend request accepted",
                body="{} is now your friend".format(instance.to_account.username),
                data={"type": "friend-request-accepted"}
            )
    instance.reset_tracker()
