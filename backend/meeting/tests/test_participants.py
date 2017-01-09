from django.contrib.auth import get_user_model
from rest_framework import status

from meeting.models import Participant, Meeting
from test_utils import APIEndpointTestCase, API_V1, authenticated


class ParticipantsDetailsEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "meetings/participants/{}/"

    def setUp(self):
        super().setUp()

        friend = get_user_model().objects.create_user(
            email="jack@test.com",
            password=None,
        )
        friend.save()

        self.meeting = Meeting(organiser=friend)
        self.meeting.save()

        self.participant = Participant(meeting=self.meeting, user=self.user)
        self.participant.save()

    def test_cannot_access_participant_unauthenticated(self):
        self.assertEqual(
            self.put(dict(), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    @authenticated
    def test_cannot_update_other_participant(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password=None,
        )
        participant = Participant(meeting=self.meeting, user=user)
        participant.save()

        self.assertEqual(
            self.put(dict(), url=self.url.format(participant.id)).status_code,
            status.HTTP_403_FORBIDDEN
        )

    @authenticated
    def test_can_accept_meeting(self):
        self.assertEqual(
            self.put(dict(accepted=True), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(Participant.objects.get(user=self.participant.id).accepted)

    @authenticated
    def test_can_refuse_meeting(self):
        self.assertEqual(
            self.put(dict(accepted=False), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertFalse(Participant.objects.get(user=self.participant.id).accepted)

    @authenticated
    def test_can_cancel_meeting(self):
        self.participant.accepted = True
        self.participant.save()

        self.assertEqual(
            self.put(dict(accepted=False), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertFalse(Participant.objects.get(user=self.participant.id).accepted)

    @authenticated
    def test_cannot_update_refused_meeting(self):
        self.participant.accepted = False
        self.participant.save()

        self.assertEqual(
            self.put(dict(), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_can_be_arrived_to_meeting(self):
        self.participant.accepted = True
        self.participant.save()

        self.assertEqual(
            self.put(dict(arrived=True), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(Participant.objects.get(user=self.participant.id).arrived)

    @authenticated
    def test_cannot_be_arrived_to_meeting_without_accepted(self):
        self.assertEqual(
            self.put(dict(arrived=True), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertFalse(Participant.objects.get(user=self.participant.id).arrived)

    @authenticated
    def test_cannot_set_not_arrived(self):
        self.assertEqual(
            self.put(dict(arrived=False), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_cannot_update_finished_meeting(self):
        self.meeting.status = Meeting.STATUS_ENDED
        self.meeting.save(update_fields=("status",))

        self.assertEqual(
            self.put(dict(), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_cannot_update_canceled_meeting(self):
        self.meeting.status = Meeting.STATUS_CANCELED
        self.meeting.save(update_fields=("status",))

        self.assertEqual(
            self.put(dict(), url=self.url.format(self.participant.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )
