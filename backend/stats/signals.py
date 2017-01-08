"""
Contains all signal handlers from the `stats` module.

We especially override the default action for the `user_logged_in` signal
as we want to be able to add the user to the list of users having logged in the current month
if he didn't have before.
"""

from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.db.models import F
from django.dispatch import receiver
from django.utils.datetime_safe import date

from stats.models import UserActiveInMonth

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"

user_logged_in.disconnect(update_last_login)


@receiver(user_logged_in)
def handle_user_logged_in(sender, user, **kwargs):
    """Add the user to the list of people having logged in this month and then execute the default action."""
    month = date.today().replace(day=1)

    if user.last_login is None or month > user.last_login:
        actives, _ = UserActiveInMonth.objects.get_or_create(month=month)
        actives.users = F('users') + 1
        actives.save()

    update_last_login(sender, user, **kwargs)
