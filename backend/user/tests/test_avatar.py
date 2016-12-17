import os
from django.conf import settings

from rest_framework import status

from user.models import User
from test_utils import authenticated, API_V1, APIEndpointTestCase
from user.tests import get_image_file


class UserAvatarEndpointTestCase(APIEndpointTestCase):
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
        response = self.client.get("{}users/me/".format(API_V1), format="json").json()
        self.assertIsNotNone(response.get("avatar"))
        self.assertEqual(self.client.get(response.get("avatar")).status_code, status.HTTP_200_OK)

    @authenticated
    def test_avatar_created_is_renamed(self):
        avatar = self.client.put(self.url, {"avatar": get_image_file()}, format="multipart").json()["avatar"]
        filename = os.path.splitext(os.path.basename(avatar))[0]
        self.assertEqual(filename, str(self.user.id), msg="Avatar file should have been renamed to the id of the user")

    @authenticated
    def test_avatar_created_is_resized(self):
        self.client.put(self.url, {"avatar": get_image_file(size=(2000, 2000))}, format="multipart")
        self.assertEqual((self.user.avatar.height, self.user.avatar.width), settings.THUMBNAILS_SIZE)
