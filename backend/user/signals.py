"""Contains all signal handlers from the `users` module."""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice

from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(pre_save, sender=FCMDevice)
def create_device(instance, **kwargs):
    """
    Fired when a new device is created.

    It remove eventual devices already attached to the current logged in user.
    """
    FCMDevice.objects.filter(user_id=instance.user_id).delete()


@receiver(post_save, sender=Friendship)
def create_friendship(instance, **kwargs):
    """
    Fired when a new friend request is created.

    Send a push notification to the user who need to accept/refuse the request.
    """
    device = instance.to_account.get_device()
    if device is not None:
        device.send_message(
            title="New friend request",
            body="{} wants to be your friend".format(instance.from_account.username),
            data={"type": "friend-request"}
        )
