"""This module defines the routes available in the `user` application."""


from django.core.exceptions import SuspiciousOperation
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from auth.permissions import IsAuthenticatedXorPost
from user.models import User, Friendship
from user.serializers import PublicUserSerializer, UserProfileSerializer, UserAvatarSerializer, FriendSerializer, \
    FriendDetailsSerializer

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class FriendViewMixin:
    """This is a simple mixin for view that require a `FriendSerializer` as serializer_class."""

    serializer_class = FriendSerializer


class UsersListView(ListCreateAPIView):
    """
    Returns all users registered in the application or create a new user.

    This view requires users to be authenticated for GET requests and NOT authenticated for POST requests.

    This view supports multiple formats : JSon, XML, etc.

    GET requests:
        With GET requests, this view accepts three request parameters to allow filtering :

            - email: to filter users by email
            - username: to filter users by username
            - phone (list): to filter users by phone number

        The `phone` filter accepts a single number or a list of numbers.

        An example of data received, in JSon:

            [
                {
                    "username": "Bob",
                    "avatar": "http://my_avatar_url"
                },
                ...
            ]

    POST requests:
        POST requests here allows the creation of new users.

        The view expects the following parameters (example in JSon):

            {
                "username": "Bill",
                "password": "MyPassword",
                "email": "Bill@me.com" (this must be unique)
            }
    """

    permission_classes = (IsAuthenticatedXorPost,)
    serializer_class = PublicUserSerializer

    available_parameters = ["email", "username", "phone"]

    def get_queryset(self):
        """
        Get the list of all users filtered accordingly.

        This returns all users that are active and can be fine-tuned with three parameters
        that are taken in `request.query_params`. These are :

            - email to filter by email
            - username to filter by username
            - phone that can be either a single entry or a list of phone numbers

        :return: the list of all users filtered by the parameters given
        """
        for param in self.request.query_params.keys():
            if param not in self.available_parameters:
                raise SuspiciousOperation({"reason": "Unrecognized query parameter: {}".format(param)})

        queryset = User.objects\
            .filter(is_active=True)\
            .exclude(id=self.request.user.id)\
            .exclude(id__in=[f.id for f in self.request.user.friends.all()])

        email = self.request.query_params.get("email")
        username = self.request.query_params.get("username")
        phone_numbers = self.request.query_params.getlist("phone")

        if email is not None:
            queryset = queryset.filter(email__icontains=email)

        if username is not None:
            queryset = queryset.filter(username__icontains=username)

        if len(phone_numbers) > 0:
            queryset = queryset.filter(phone_number__in=[User.hash_phone_number(phone) for phone in phone_numbers])

        return queryset


class UserProfileView(RetrieveUpdateAPIView):
    """
    Allows a user to manage his profile.

    This view requires the user to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    An example of data, in JSon is :

        {
            "username": "MyUsername" (this is required)
            "email": "MyEmail" (this is required)
            "avatar": "AvatarUrl" (this is read-only, optional)
            "password": "Password" (this is write-only)
            "phone_number": "MyPhoneNumber" (this is write-only, optional, respecting the E.164 format)
            "country": "CH"  (this is write-only, optional, and must be sent when sending `phone_number`)
        }
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = User.objects.filter(is_active=True)

    def get_object(self):
        """Get the current user on which to perform work."""
        return self.request.user

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request to the correct request.

        This view systematically adds a csrf token to the request, as the web frontend always gets this link at first.

        This allows us to be sure the csrf token is available for our web frontend.

        :param request: request that is made
        """
        return super().dispatch(request, *args, **kwargs)


class UserAvatarView(UpdateAPIView, DestroyAPIView):
    """
    Allows to update the logged in user's avatar.

    This view requires the user to be authenticated.

    Update the avatar :
        To update the avatar, send a multipart request, with an attribute file which contains the new avatar to use.

        - On success will return a 201 CREATED
        - On error will send a 400, 401, or 403 depending on the error, with a message explaining it.

    To delete the avatar send a DELETE request.

        - On success will return a 204 NO-CONTENT
        - On error will send a 400, 401, or 403 depending on the error, with a message explaining it.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserAvatarSerializer
    queryset = User.objects.filter(is_active=True)
    parser_classes = (MultiPartParser, FileUploadParser)

    def get_object(self):
        """Get the current user on which to perform work."""
        return self.request.user

    # noinspection PyMethodMayBeStatic
    def perform_destroy(self, instance):
        """Remove the user's avatar."""
        instance.avatar.delete()
        instance.last_avatar_update = timezone.now()
        instance.save()


class FriendListView(FriendViewMixin, ListCreateAPIView):
    """
    Returns user's friends that have accepted the request and that are not blocked by the user.

    This view requires to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    GET requests:
        An example of data received, in JSon:

            [
                {
                    "friend": {
                        "username": "Bob",
                        "avatar": "http://my_avatar_url"
                    },
                    is_hidden: False,
                    is_accepted: True,
                    is_blocked: False
                },
                ...
            ]

    POST requests:
        POST requests here allows the creation of new friendships. Note that these need the second user's agreement.

        The view expects the following parameters (example in JSon):

            {
                "friend": friend_id
            }
    """

    def get_queryset(self):
        """Get the queryset of all friends currently active, that is accepted and not blocked by the current user."""
        return Friendship.objects.filter(is_accepted=True).filter(
            Q(from_account=self.request.user, from_blocking=False) |
            Q(to_account=self.request.user, to_blocking=False)
        )


class AllFriendListView(FriendViewMixin, ListAPIView):
    """
    Returns user's friends whether they already accepted the request or not, whether they are blocked or not.

    This view requires to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    An example of data received, in JSon:

        [
            {
                "friend": {
                    "username": "Bob",
                    "avatar": "http://my_avatar_url"
                },
                is_hidden: True,
                is_accepted: False,
                is_blocked: False
            },
            {
                "friend": {
                    "username": "Bill",
                    "avatar": none
                },
                is_hidden: False,
                is_accepted: True,
                is_blocked: True
            },

            ...
        ]
    """

    def get_queryset(self):
        """Get all friends and friends requests the current user made."""
        return Friendship.objects.filter(Q(from_account=self.request.user) | Q(to_account=self.request.user))


class PendingFriendListView(FriendViewMixin, ListAPIView):
    """
    Returns all friends requests made to the user that where not yet answered.

    This view requires to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    An example of data received, in JSon:

        [
            {
                "friend": {
                    "username": "Bob",
                    "avatar": "http://my_avatar_url"
                },
                is_hidden: False,
                is_accepted: False,
                is_blocked: False
            },

            ...
        ]
    """

    def get_queryset(self):
        """Get all unanswered friend requests for the current user."""
        return Friendship.objects.filter(to_account=self.request.user, is_accepted=False, is_hidden=False)


class HiddenPendingFriendListView(FriendViewMixin, ListAPIView):
    """
    Returns all friends requests made to the user that where not yet answered and marked as hidden.

    This view requires to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    An example of data received, in JSon:

        [
            {
                "friend": {
                    "username": "Bob",
                    "avatar": "http://my_avatar_url"
                },
                is_hidden: True,
                is_accepted: False,
                is_blocked: False
            },

            ...
        ]
    """

    def get_queryset(self):
        """Get all friend request that the user has hidden."""
        return Friendship.objects.filter(to_account=self.request.user, is_accepted=False, is_hidden=True)


class BlockedFriendListView(FriendViewMixin, ListAPIView):
    """
    Returns all friends that the user has blocked.

    This view requires to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    An example of data received, in JSon:

        [
            {
                "friend": {
                    "username": "Bob",
                    "avatar": "http://my_avatar_url"
                },
                is_hidden: False,
                is_accepted: False,
                is_blocked: True
            },

            ...
        ]
    """

    def get_queryset(self):
        """Get all friends that the current user has blocked."""
        return Friendship.objects.filter(
            Q(to_account=self.request.user, to_blocking=True) | Q(from_account=self.request.user, from_blocking=True)
        )


class FriendListDetailsView(RetrieveUpdateAPIView):
    """
    Allows a user to manage a friendship link.

    This view requires the user to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    Acceptable entries are :
        "is_accepted": accepts a boolean, can only be set to True to accept a friendship relation.
        "is_blocked": accepts a boolean, block or unblock a friend
        "is_hidden": accepts a boolean, hides or un-hides an unaccepted friend request.

    GET requests will return something like (in JSon):

        {
            "friend": {
                "username": "Bob",
                "avatar": "http://my_avatar_url"
            },
            is_hidden: False,
            is_accepted: False,
            is_blocked: True
        },
    """

    serializer_class = FriendDetailsSerializer

    def get_queryset(self):
        """Get all friendship links the current user has."""
        return Friendship.objects.filter(Q(from_account=self.request.user) | Q(to_account=self.request.user))
