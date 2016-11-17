import random
import uuid

from fcm_django.models import FCMDevice
from rest_framework import status

from user.tests import APIEndpointTestCase, authenticated

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class UserDeviceEndpointTestCase(APIEndpointTestCase):
    format = "json"
    url = "/fcm/devices/"

    @staticmethod
    def generate_device():
        return dict(
            registration_id="registration-id-{}".format(uuid.uuid4()),
            type=random.choice(["android", "ios"]),
        )

    # Post Operations on /
    # this allows the creation of devices

    def test_must_be_logged_in_to_create_device(self):
        self.assertEqual(self.client.put(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_creating_device_requires_registration_id(self):
        self.assert400WithError(self.post(dict()), "registration_id")

    @authenticated
    def test_can_create_device(self):
        self.assertEqual(self.post(self.generate_device()).status_code, status.HTTP_201_CREATED)

    @authenticated
    def test_cannot_create_already_existing_device(self):
        device = self.generate_device()
        self.post(device)
        self.assertContains(self.post(device), "field must be unique", status_code=status.HTTP_400_BAD_REQUEST)

    @authenticated
    def test_created_device_is_set_to_me(self):
        device = self.generate_device()
        self.post(device)
        self.assertEqual(FCMDevice.objects.select_related("user").get(registration_id=device["registration_id"]).user.id, self.user.id)

    @authenticated
    def test_created_device_replaced_old_one(self):
        device1 = self.generate_device()
        device2 = self.generate_device()
        self.post(device1)
        self.post(device2)
        with self.assertRaises(FCMDevice.DoesNotExist):
            FCMDevice.objects.get(registration_id=device1["registration_id"])
        self.assertEqual(FCMDevice.objects.select_related("user").get(registration_id=device2["registration_id"]).user.id, self.user.id)
