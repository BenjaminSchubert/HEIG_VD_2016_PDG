import os

from rest_framework import status

from user.models import User
from user.tests import authenticated, API_V1, get_image_file, APIEndpointTestCase


class UserAvatarEndpointTestCase(APIEndpointTestCase):
    format = "json"
    url = API_V1 + "users/me/avatar/"

    def test_must_be_authenticated(self):
        self.assertEqual(self.client.put(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_send_avatar_image(self):
        response = self.client.put(self.url, {"avatar": get_image_file()}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(User.objects.get(email=self.user.email).avatar)

    @authenticated
    def test_last_avatar_date_is_updated_on_avatar_update(self):
        self.client.put(self.url, {"avatar": get_image_file()}, format="multipart")
        old_date = User.objects.get(email=self.user.email).last_avatar_update

        self.client.put(self.url, {"avatar": get_image_file()}, format="multipart")
        new_date = User.objects.get(email=self.user.email).last_avatar_update

        self.assertGreater(
            new_date, old_date, msg="the avatar update date is not greater than the avatar creation date"
        )

    @authenticated
    def test_can_remove_avatar_image(self):
        self.client.put(self.url, {"avatar": get_image_file()}, format="multipart")
        self.assertEqual(self.client.delete(self.url, format="json").status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.get(email=self.user.email).avatar)

    @authenticated
    def test_can_retrieve_avatar_image(self):
        self.client.put(self.url, {"avatar": get_image_file()}, format="multipart")
        response = self.client.get("{}users/?email={}".format(API_V1, self.user.email), format="json").json()
        self.assertEqual(len(response), 1)
        self.assertIsNotNone(response[0].get("avatar"))
        self.assertEqual(self.client.get(response[0].get("avatar")).status_code, status.HTTP_200_OK)

    @authenticated
    def test_avatar_created_is_renamed(self):
        avatar = self.client.put(self.url, {"avatar": get_image_file()}, format="multipart").json()["avatar"]
        filename = os.path.splitext(os.path.basename(avatar))[0]
        self.assertEqual(filename, str(self.user.id), msg="Avatar file should have been renamed to the id of the user")
