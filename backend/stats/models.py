"""Contains all models from the `meeting` module."""

from django.db import models


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class UserActiveInMonth(models.Model):
    """This model contains information about users that logged in during a given month."""

    month = models.DateField(primary_key=True)
    users = models.PositiveIntegerField(default=0)
