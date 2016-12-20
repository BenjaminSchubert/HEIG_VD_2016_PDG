from rest_framework import status

from device.models import Device
from device.tests import generate_device_info, create_device
from test_utils import APIEndpointTestCase, API_V1, authenticated
from user.models import User

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DevicesEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "fcm/devices/"
    number_of_other_users = 1

    # Post Operations on /
    # this allows the register a device with the current logged in user

    def test_must_be_logged_in_to_register_device(self):
        self.assertEqual(self.client.put(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_register_device_requires_registration_id(self):
        self.assert400WithError(self.post(dict()), "registration_id")

    @authenticated
    def test_can_register_device(self):
        self.assertEqual(self.post(generate_device_info()).status_code, status.HTTP_201_CREATED)

    @authenticated
    def test_register_my_existing_device_has_no_effect(self):
        device = generate_device_info()
        self.post(device)
        self.assertEqual(self.post(device).status_code, status.HTTP_204_NO_CONTENT)

    @authenticated
    def test_cannot_register_already_existing_device(self):
        device1 = generate_device_info()

        device2 = device1.copy()
        device2["user"] = User.objects.last()
        Device(**device2).save()

        self.assertContains(self.post(device1), "already exists", status_code=status.HTTP_400_BAD_REQUEST)

    @authenticated
    def test_registered_device_is_set_to_me(self):
        device = generate_device_info()
        self.post(device)
        self.assertEqual(
            Device.objects.get(registration_id=device["registration_id"]).user_id,
            self.user.id
        )

    @authenticated
    def test_registered_device_replaced_old_one(self):
        device1 = create_device(self.user)
        device2 = create_device(self.user)

        # The old device should not exist anymore
        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(registration_id=device1.registration_id)

        # My device should be the new one
        self.assertEqual(
            Device.objects.get(registration_id=device2.registration_id).user_id,
            self.user.id
        )
