"""This module defines the routes available in the `device` application."""

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from device.models import Device
from device.serializers import DeviceSerializer

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeviceView(CreateAPIView):
    """
    Allow to register a new device, related to the current logged in user.

    This view requires the user to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    POST requests:
        POST requests here allows the registration of new devices.

        The view expects the following parameters (example in JSon):

            {
                "registration_id": "MyRegistrationId"
            }

        - On success will return a 201 CREATED
        - On error will send a 400, 401 depending on the error, with a message explaining it.
        - If the registration_id is already set with the current user, no action will be done
          and a 204 NO CONTENT will be returned. It simplify devices registration.

    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new device.

        If a corresponding device is already attached with the current logged in user,
        don't try to save and simply return a 204 response.

        :param request: the HTTP request done
        :return a 400, 401, 201, 204 response depending on whether the data was correct or not.
        """
        if "registration_id" in request.data:
            device = Device.objects.filter(
                Q(registration_id=request.data["registration_id"]) &
                Q(user=self.request.user)
            ).first()
            if device is not None:
                return Response(status=status.HTTP_204_NO_CONTENT)

        return super(DeviceView, self).create(request, *args, **kwargs)
