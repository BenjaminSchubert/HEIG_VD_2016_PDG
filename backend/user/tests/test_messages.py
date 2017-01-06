from unittest.mock import ANY

from django.contrib.auth import get_user_model

from device.tests import create_device, MockFcmMessagesMixin, generate_device_info
from test_utils import APIEndpointTestCase, API_V1, authenticated
from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(MockFcmMessagesMixin, APIEndpointTestCase):
    number_of_other_users = 1

    def setUp(self):
        super().setUp()

        for user in get_user_model().objects.all():
            create_device(user)

        self.mocked_send_fcm_message.reset_mock()

    @authenticated
    def test_new_friendship_send_push_notification(self):
        friend = get_user_model().objects.get(id=2)

        self.post(dict(friend=friend.id), url=API_V1 + "users/friends/")

        self.mocked_send_fcm_message.assert_called_once_with(
            registration_id=friend.get_device().registration_id,
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "friend-request"},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_accept_friendship_send_push_notification(self):
        friend = get_user_model().objects.get(id=2)
        friendship = Friendship(from_account=friend, to_account=self.user)
        friendship.save()

        self.mocked_send_fcm_message.reset_mock()

        self.put(dict(is_accepted=True), url=API_V1 + "users/friends/{}/".format(friendship.id))

        self.mocked_send_fcm_message.assert_called_once_with(
            registration_id=friend.get_device().registration_id,
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "friend-request-accepted"},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_try_to_send_deferred_messages_on_device_registration(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)

        device = self.user.get_device()
        device.send_message()
        device.send_message()

        self.mocked_send_fcm_message.reset_mock()
        self.mocked_send_fcm_message.return_value = dict(success=1)

        self.post(generate_device_info(), url=API_V1 + "fcm/devices/")

        self.assertEqual(self.mocked_send_fcm_message.call_count, 2)
