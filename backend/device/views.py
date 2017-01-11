"""This module defines the routes available in the `device` application."""
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

        - On success will return a 201 CREATED or 200 OK if the device was already attached with the user.
        - On error will send a 400, 401 depending on the error, with a message explaining it.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DeviceSerializer

    def create(self, request, *args, **kwargs):
        """
        Override the create method.

        If the user is registering the same device than he already has,
        just try to send eventually pending messages and response with a HTTP 200 code.

        If the device is already attached to an other user, change it for the current one.

        Otherwise, register the new device.

        :param request: the HTTP request done
        :return a 201, 200, 400, 401 response depending on whether the data was correct or not.
        """
        Device.objects.filter(user=self.request.user).delete()
        if "registration_id" in self.request.data:
            try:
                device = Device.objects.get(registration_id=self.request.data["registration_id"])
                device.user = self.request.user
                device.save(update_fields=("user",))
                self.request.user.send_deferred_messages()
                return Response(status=status.HTTP_201_CREATED)
            except Device.DoesNotExist:
                pass
        return super(DeviceView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Override method to set the current user."""
        serializer.validated_data["user"] = self.request.user
        return super(DeviceView, self).perform_create(serializer)
