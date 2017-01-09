from unittest.mock import ANY

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status

from device.tests import create_device, MockFcmMessagesMixin
from meeting.models import Meeting, Participant
from meeting.tests import create_meeting
from test_utils import APIEndpointTestCase, API_V1, authenticated
from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class TestPositionsEndpoint(MockFcmMessagesMixin, APIEndpointTestCase):
    url = API_V1 + "meetings/positions/"

    number_of_other_users = 5

    def setUp(self):
        super().setUp()
        self.longitude = 0.171
        self.latitude = 0.155

        for user in get_user_model().objects.all():
            create_device(user)
            Friendship(from_account=self.user, to_account=user, is_accepted=True).save()

        self.mocked_send_fcm_message.reset_mock()

    def test_cannot_post_position_when_unauthenticated(self):
        self.assertEqual(self.post(dict()).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_post_position(self):
        self.assertEqual(
            self.post(dict(latitude=self.latitude, longitude=self.longitude)).status_code,
            status.HTTP_201_CREATED
        )

    @authenticated
    def test_can_post_position_send_push_notification(self):
        """
        No message for actuator and users who declined the meeting or have not yet answered.
        """
        meeting = create_meeting(self.user)
        meeting.status = Meeting.STATUS_PROGRESS
        meeting.save(update_fields=("status",))

        my_participant = Participant.objects.get(user=self.user)
        my_participant.accepted = True
        my_participant.save(update_fields=("accepted",))

        other_participants = meeting.participants\
            .filter(~Q(id=self.user.id) & Q(participant__accepted=True))\
            .all()

        self.mocked_send_fcm_bulk_message.reset_mock()

        self.post(dict(latitude=self.latitude, longitude=self.longitude))

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in other_participants],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={
                "type": "user-position-update",
                "meeting": meeting.id,
                "participant": my_participant.id
            },
            sound=ANY,
            badge=ANY,
        )

