import unittest

from rest_framework import status

from user.tests import APIEndpointTestCase, authenticated
from user.tests import API_V1


class UserProfileEndpointTestCase(APIEndpointTestCase):
    format = "json"
    url = API_V1 + "users/me/"

    def test_must_be_logged_in_to_update_information(self):
        self.assertEqual(self.put(dict()).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_retrieve_own_information(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.json(),
            dict(username=self.user.username, email=self.user.email, phone_number=None, avatar=None)
        )

    @authenticated
    def test_can_update_information(self):
        response = self.put(dict(username="goatsy", email=self.user.email))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "goatsy")

    @authenticated
    def test_can_login_after_update_without_password_field(self):
        self.put(dict(username="goatsy", email=self.user.email))
        self.assertTrue(self.client.login(email=self.user.email, password=self.password))

    @authenticated
    def test_can_login_after_password_update(self):
        self.put(dict(username="goatsy", email=self.user.email, password="new"))
        # check can't login with old password
        self.assertFalse(self.client.login(email=self.user.email, password=self.password))
        # check can login with new password
        self.assertTrue(self.client.login(email=self.user.email, password="new"))

    @unittest.skip("Phone number is not yet implemented correctly")
    @authenticated
    def test_phone_number_is_obfuscated(self):
        raise NotImplementedError()
