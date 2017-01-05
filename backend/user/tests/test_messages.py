from unittest.mock import patch, ANY

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.tests import create_device, MockFcmMessagesMixin
from user.models import Friendship, User

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(MockFcmMessagesMixin, TestCase):

    def setUp(self):
        super().setUp()

        for i in range(2):
            user = get_user_model().objects.create_user(
                username="user-{}".format(i),
                email="email-{}@test.com".format(i),
            )
            create_device(user)

        self.mocked_send_fcm_message.reset_mock()

    def test_new_friendship_send_push_notification(self):
        u1 = User.objects.first()
        u2 = User.objects.last()
        Friendship(from_account=u1, to_account=u2).save()

        self.mocked_send_fcm_message.assert_called_once_with(
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

    def test_try_to_send_deferred_messages_on_device_registration(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)
        user = User.objects.first()
        device = user.get_device()
        device.send_message()
        device.send_message()

        self.mocked_send_fcm_message.reset_mock()
        self.mocked_send_fcm_message.return_value = dict(success=1)
        create_device(user)

        self.assertEqual(self.mocked_send_fcm_message.call_count, 2)
