from unittest.mock import patch, ANY

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.tests import create_device
from user.models import Friendship, User

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(TestCase):

    def setUp(self):
        super().setUp()

        for i in range(2):
            user = get_user_model().objects.create_user(
                username="user-{}".format(i),
                email="email-{}@test.com".format(i),
            )
            create_device(user)

    @patch("device.models.send_fcm_message")
    def test_new_friendship_send_push_notification(self, mocked_handler):
        u1 = User.objects.first()
        u2 = User.objects.last()
        Friendship(from_account=u1, to_account=u2).save()

        mocked_handler.assert_called_once_with(
            registration_id=u2.get_device().registration_id,
            title=ANY,
            body=ANY,
            data={"type": "friend-request"},
        )

    def test_accept_friendship_send_push_notification(self):
        u1 = User.objects.first()
        u2 = User.objects.last()
        friendship = Friendship(from_account=u1, to_account=u2)
        friendship.save()

        with patch("device.models.send_fcm_message") as mocked_handler:
            friendship.is_accepted = True
            friendship.save()

        mocked_handler.assert_called_once_with(
            registration_id=u1.get_device().registration_id,
            title=ANY,
            body=ANY,
            data={"type": "friend-request-accepted"},
        )

    @patch("device.models.send_fcm_message")
    def test_try_to_send_deferred_messages_on_device_registration(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        user = User.objects.first()
        device = user.get_device()
        device.send_message()
        device.send_message()

        mocked_handler.reset_mock()
        mocked_handler.return_value = dict(success=1)
        create_device(user)

        self.assertEqual(mocked_handler.call_count, 2)
