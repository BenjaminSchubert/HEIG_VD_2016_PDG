"""
Contains all models from the `user` module.

We override here the default django user model and extend it.
"""


import hashlib

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db import transaction
from popo_attribute_tracker.attribute_tracker import AttributeTrackerMixin

from device.models import Device, DeferredMessage

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class AccountManager(BaseUserManager):
    """Overrides the default UserManager with our custom one."""

    @transaction.atomic
    def _create_user(self, password=None, phone_number=None, **fields):
        user = self.model(**fields)

        user.set_password(password)
        user.set_phone_number(phone_number)
        user.save()
        return user

    def create_user(self, **fields):
        """
        Create a new user.

        :param fields: fields when creating user
        :return: the new user instance
        """
        fields.setdefault('is_staff', False)
        fields.setdefault('is_superuser', False)

        return self._create_user(**fields)

    def create_superuser(self, **fields):
        """
        Create a new superuser.

        This user will have all rights available, at any time

        :param fields: additional fields when creating user
        :return: the new user instance
        """
        fields.setdefault('is_staff', True)
        fields.setdefault('is_superuser', True)

        if fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(**fields)

    def get_queryset(self):
        """Provide a custom QuerySet for users."""
        return UserQuerySet(self.model)


class UserQuerySet(models.query.QuerySet):
    """
    Overrides the default QuerySet with our custom one.

    Provide a function to send a message to a QuerySet (a selection of users).
    """

    def send_message(self, title=None, body=None, type=None, deferred=True):
        """
        Send a push message to the users.

        :param title: the title of the message
        :param body: the body of the message
        :param type: the type of the message
        :param deferred: define if message can be deferred or not
        """
        Device.objects.filter(user__in=self.all()).send_message(title, body, type, deferred)


class User(AbstractBaseUser, PermissionsMixin):
    """Extends `AbstractBaseUser` to accommodate the User model to our needs."""

    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.BinaryField(max_length=255, unique=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True)
    last_avatar_update = models.DateTimeField(auto_now_add=True)
    hidden = models.DateTimeField(null=True, default=None)

    friends = models.ManyToManyField("User", through="Friendship")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    objects = AccountManager()

    def get_full_name(self):
        """Get user's full name."""
        return "{} {}".format(self.last_name, self.first_name)

    def get_short_name(self):
        """Get user's short name."""
        return self.username

    def set_phone_number(self, phone_number: str):
        """
        Set user's phone number securely, by hashing it.

        :param phone_number: original phone number
        """
        if phone_number is not None:
            self.phone_number = User.hash_phone_number(phone_number)
        else:
            self.phone_number = None

    @staticmethod
    def hash_phone_number(number):
        """
        Hash the given phone number.

        :param number: phone number to hash
        :return: hashed phone number
        """
        return hashlib.pbkdf2_hmac("sha512", number.encode("utf8"), settings.SECRET_KEY.encode("utf8"), 10000)

    def get_device(self):
        """
        Get the user unique device or None.

        :return: reference to the device
        """
        return Device.objects.filter(user=self).first()

    def send_message(self, title=None, body=None, type=None, deferred=True):
        """
        Send a push message to the device of the user.

        :param title: the title of the message
        :param body: the body of the message
        :param type: the type of the message
        :param deferred: define if message can be deferred or not
        """
        device = self.get_device()
        if device is not None:
            device.send_message(title, body, type, deferred)

    def send_deferred_messages(self):
        """
        Try to send eventually pending push notifications to the current registered device.

        Stop on first failed sent.
        """
        device = self.get_device()
        if device is not None:
            for message in DeferredMessage.objects.filter(user=self):
                if device.send_deferred_message(message) is False:
                    return


class Friendship(models.Model, AttributeTrackerMixin):
    """Extends `Model` to keep information about friends."""

    from_account = models.ForeignKey(User, related_name="from_account")
    to_account = models.ForeignKey(User, related_name="to_account")
    unique_validator = models.CharField(max_length=255, unique=True)
    is_accepted = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    from_blocking = models.BooleanField(default=False)
    to_blocking = models.BooleanField(default=False)

    TRACKED_ATTRS = ("is_accepted",)

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Save the friendship instance.

        This will beforehand create a `unique_validator` field based on both user ids.

        This is to ensure that two requests cannot target the two same users.

        The `unique` field on ('from_account', 'to_account') would not be sufficient as a user can add the second
        and the second can add the first one. This is therefore the safest, concurrency-proof way of doing it.
        """
        self.unique_validator = "{min}{max}".format(
            min=min(self.from_account.id, self.to_account.id),
            max=max(self.from_account.id, self.to_account.id)
        )

        super().save(force_insert, force_update, using, update_fields)
