"""This module defines the routes available in the `admin` application."""

from django.contrib.auth import get_user_model
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser

from admin.serializers import UserSerializer

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class UserListView(ListAPIView):
    """
    Get the list of all users in the application with their rights.

    This view will return 200 OK if the user has the rights, with the payload described below. Otherwise it will
    return 403 FORBIDDEN.

    This view supports multiple formats: JSon, XML, etc.

    This view only supports GET requests, and will returns data with the following format (json example):

        [
            {
                "username": "Bob",
                "email": "bob@rady.com",
                "is_staff": true,
                "is_active": true,
                "id": 2,
            },
            ...
        ]
    """

    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class UserDetailsView(UpdateAPIView):
    """
    Update the given user's rights.

    This view allows an administrator to update the rights of a user.

    This view will return 200 OK if the update could be done.
    It will return 404 NOT FOUND if no user with the given ID exists.
    It will return 403 FORBIDDEN if the logged in user is not administrator.

    It only supports PUT requests, and expect the following parameters:

        - is_staff: boolean indicating whether the user is to be staff or not
        - is_active: boolean indicating whether the user can login or not

    This view supports multiple formats: JSon, XML, etc.


    An example request, in json is :

        {
            "is_active": True,
            "is_staff": True,
        }
    """

    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
