"""This module defines the routes available in the `user` application."""


from django.core.exceptions import SuspiciousOperation
from django.utils import timezone
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from auth.permissions import IsAuthenticatedXorPost
from user.models import User
from user.serializers import PublicUserSerializer, UserProfileSerializer, UserAvatarSerializer


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


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

        queryset = User.objects.filter(is_active=True)

        email = self.request.query_params.get("email")
        username = self.request.query_params.get("username")
        phone_numbers = self.request.query_params.getlist("phone")

        if email is not None:
            queryset = queryset.filter(email__contains=email)

        if username is not None:
            queryset = queryset.filter(username__contains=username)

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
        }
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    queryset = User.objects.filter(is_active=True)

    def get_object(self):
        """Get the current user on which to perform work."""
        return self.request.user


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

    def perform_destroy(self, instance):
        """Remove the user's avatar."""
        instance.avatar.delete()
        instance.last_avatar_update = timezone.now()
        instance.save()
