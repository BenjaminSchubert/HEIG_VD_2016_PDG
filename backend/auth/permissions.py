"""
Declares various permission types not in the base framework.

This allows us to have a more fine-grained control over the permissions of our views.
"""

from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuthenticatedXorPost(BasePermission):
    """
    Permission scheme allowing unauthenticated users to do `POST` requests, while restraining others from doing it.

    This will allow every other method to authenticated users.
    """

    def has_permission(self, request, view):
        """
        Get whether the user has the permission required to call this view, with this method.

        :param request: request that was done
        :param view: requested view
        :return: `True` if access is authorized, `False` otherwise
        """
        if request.method == "POST":
            return not (request.user and is_authenticated(request.user))

        return request.user and is_authenticated(request.user)


class CanEditParticipant(IsAuthenticated):

    def has_object_permission(self, request, view, obj):

        return request.user.id == obj.user_id


class CanViewXorOwnMeeting(IsAuthenticated):

    def has_object_permission(self, request, view, obj):

        if request.method == "PUT" or request.method == "PATCH":
            return request.user.id == obj.organiser_id

        return obj.participant_set.filter(user_id=request.user.id, meeting_id=obj.id).count() == 1
