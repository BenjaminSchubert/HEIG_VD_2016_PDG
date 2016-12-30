"""Contains all signal handlers from the `user` module."""

from django.db.models.signals import post_init, post_save
from django.dispatch import receiver

from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


@receiver(post_init, sender=Friendship)
def post_init_friendship(instance, **kwargs):
    """
    Fired when instantiate a friendship object model, signal sent at the end of the model init method.

    It initialize the attribute tracker for the Friendship model.
    """
    instance.initialize_tracker()


@receiver(post_save, sender=Friendship)
def post_save_friendship(instance, created, **kwargs):
    """
    Fired when friendship relation is saved (created or updated).

    Creation :
    - Send a push notification to the user who need to accept/refuse the request.
    Update, if the friendship has been accepted :
    - Send a push notification to the user who asked for the friendship that the relation has been accepted.
    """
    if created:
        instance.to_account.send_message(
            title="New friend request",
            body="{} wants to be your friend".format(instance.from_account.username),
            type="friend-request",
        )
    elif instance.has_changed("is_accepted") and instance.is_accepted is True:
        instance.from_account.send_message(
            title="Friend request accepted",
            body="{} is now your friend".format(instance.to_account.username),
            type="friend-request-accepted",
        )
    instance.reset_tracker()
