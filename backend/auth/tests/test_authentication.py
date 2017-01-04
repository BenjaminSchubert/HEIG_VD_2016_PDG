from rest_framework import status

from test_utils import APIEndpointTestCase, API_V1, authenticated


class AuthenticationBySessionEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "auth/session/"

    def test_can_authenticate(self):
        self.assertEqual(
            self.post(dict(username=self.user.email, password=self.password)).status_code,
            status.HTTP_200_OK
        )
        self.assertIn("_auth_user_id", self.client.session)

    @authenticated
    def test_cannot_authenticate_if_already_authenticated(self):
        self.assertEqual(self.post({}).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_logout_when_not_authenticated(self):
        self.assertEqual(self.delete().status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_logout_when_authenticated(self):
        self.client.force_login(self.user)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertEqual(self.delete().status_code, status.HTTP_200_OK)
        self.assertNotIn("_auth_user_id", self.client.session)
