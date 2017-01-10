from rest_framework import status

from user.models import User
from test_utils import APIEndpointTestCase, authenticated, API_V1


class UserProfileEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "users/me/"

    def test_must_be_logged_in_to_update_information(self):
        self.assertEqual(self.put(dict()).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_retrieve_own_information(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.json(),
            dict(id=self.user.id, username=self.user.username, email=self.user.email, avatar=None, is_hidden=False)
        )

    @authenticated
    def test_can_update_information(self):
        response = self.put(dict(username="goatsy", email=self.user.email))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "goatsy")

    @authenticated
    def test_cannot_use_same_email_as_someone_else(self):
        user2 = User.objects.create_user(username="goat", email="goat@tsy.com")
        self.assertContains(
            self.put(dict(username=self.user.username, email=user2.email)),
            "already exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )

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

    @authenticated
    def test_cannot_send_missformed_phonenumber(self):
        self.assertEqual(
            self.put(dict(username="goatsy", email=self.user.email, phone_number="abc")).status_code,
            status.HTTP_400_BAD_REQUEST,
            msg="Misformed phone number should not be accepted"
        )

    @authenticated
    def test_cannot_send_phone_number_without_country(self):
        response = self.put(dict(username="goatsy", email=self.user.email, phone_number="+41760000000"))
        self.assert400WithError(response, "country")

    @authenticated
    def test_cannot_send_country_without_phone_number(self):
        response = self.put(dict(username="goatsy", email=self.user.email, country="CH"))
        self.assert400WithError(response, "phone_number")

    @authenticated
    def test_cannot_send_valid_phonenumber_with_invalid_country(self):
        response = self.put(dict(username="goatsy", email=self.user.email, phone_number="+41760000000", country="GB"))
        self.assert400WithError(response, "phone_number")

    @authenticated
    def test_can_send_valid_phonenumber(self):
        response = self.put(dict(username="goatsy", email=self.user.email, phone_number="+41760000000", country="CH"))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="A valid phone number cannot be entered"
        )

    @authenticated
    def test_phone_number_is_obfuscated(self):
        number = "+41760000000"
        self.put(dict(username="goatsy", email=self.user.email, phone_number=number))
        self.assertNotEqual(number, self.user.phone_number, msg="The phone number should be obfuscated")
