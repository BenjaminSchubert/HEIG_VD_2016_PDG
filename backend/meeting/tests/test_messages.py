from unittest.mock import ANY, call

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.tests import create_device, MockFcmMessagesMixin
from meeting.models import Meeting, Participant
from user.models import User, Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(MockFcmMessagesMixin, TestCase):

    def setUp(self):
        super().setUp()

        users = []
        for i in range(5):
            user = get_user_model().objects.create_user(
                username="user-{}".format(i),
                email="email-{}@test.com".format(i),
            )
            create_device(user)
            users.append(user)

        for i in range(5):
            for j in range(5):
                if users[i].id > users[j].id:
                    Friendship(from_account=users[i], to_account=users[j]).save()

        self.mocked_send_fcm_message.reset_mock()

    def test_new_meeting_send_push_notifications(self):
        calls = []

        organiser = User.objects.first()
        meeting = Meeting(organiser=organiser)
        meeting.save()

        participants = User.objects.exclude(id=organiser.id)
        for participant in participants:
            Participant(meeting=meeting, user=participant).save()
            calls.append(call(
                registration_id=participant.get_device().registration_id,
                title=ANY,
                body=ANY,
                data={"type": "new-gathering"},
            ))

        self.assertEqual(self.mocked_send_fcm_message.call_count, participants.count())  # no message to organiser
        self.mocked_send_fcm_message.assert_has_calls(calls, any_order=True)
