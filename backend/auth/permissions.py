"""
Declares various permission types not in the base framework.

This allows us to have a more fine-grained control over the permissions of our views.
"""


from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission


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
