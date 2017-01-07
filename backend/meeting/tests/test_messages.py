from unittest import expectedFailure
from unittest.mock import ANY, call

from django.contrib.auth import get_user_model

from device.models import DeferredMessage
from device.tests import create_device, MockFcmMessagesMixin
from meeting.models import Meeting, Participant
from test_utils import APIEndpointTestCase, authenticated, API_V1
from user.models import Friendship

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(MockFcmMessagesMixin, APIEndpointTestCase):
    number_of_other_users = 4

    def setUp(self):
        super().setUp()

        for user in get_user_model().objects.all():
            create_device(user)
            Friendship(from_account=self.user, to_account=user, is_accepted=True).save()

        self.mocked_send_fcm_message.reset_mock()

    @authenticated
    def test_new_meeting_send_push_notifications(self):
        participants = get_user_model().objects.exclude(id=self.user.id)

        self.post(
            dict(
                type="place",
                place=dict(latitude=0, longitude=1),
                participants=participants.values_list("id", flat=True)
            ),
            url=API_V1 + "meetings/"
        )

        self.assertEqual(self.mocked_send_fcm_message.call_count, participants.count())  # no message to organiser
        self.mocked_send_fcm_message.assert_has_calls([
            call(
                registration_id=u.get_device().registration_id,
                message_title=ANY,
                message_body=ANY,
                message_icon=ANY,
                data_message={"type": "new-meeting", "meeting": Meeting.objects.first().id},
                sound=ANY,
                badge=ANY,
            )
            for u in participants
        ], any_order=True)

    @authenticated
    def test_accept_meeting_send_push_notifications(self):
        meeting = Meeting(organiser=get_user_model().objects.exclude(id=self.user.id).last())
        meeting.save()
        for user in get_user_model().objects.all():
            Participant(meeting=meeting, user=user).save()
        my_participant = Participant.objects.get(user=self.user)

        self.put(dict(accepted=True), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        users = get_user_model().objects.exclude(id=self.user.id).all()  # no message to actuator

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-accepted-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_refused_meeting_send_push_notifications(self):
        meeting = Meeting(organiser=get_user_model().objects.exclude(id=self.user.id).last())
        meeting.save()
        for user in get_user_model().objects.all():
            Participant(meeting=meeting, user=user).save()
        my_participant = Participant.objects.get(user=self.user)

        self.put(dict(accepted=False), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        users = get_user_model().objects.exclude(id=self.user.id).all()  # no message to actuator

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-refused-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_user_arrived_at_meeting_send_push_notifications(self):
        meeting = Meeting(organiser=get_user_model().objects.exclude(id=self.user.id).last())
        meeting.save()
        for user in get_user_model().objects.all():
            Participant(meeting=meeting, user=user, accepted=True).save()
        my_participant = Participant.objects.get(user=self.user)

        self.put(dict(arrived=True), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        users = get_user_model().objects.exclude(id=self.user.id).all()  # no message to actuator

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-arrived-to-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_ended_meeting_cancel_related_deferred_messages(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)

        meeting = Meeting(organiser=self.user)
        meeting.save()
        for user in get_user_model().objects.all():
            Participant(meeting=meeting, user=user, accepted=True).save()

        r = self.put(dict(status=meeting.STATUS_ENDED), url=API_V1 + "meetings/{}/".format(meeting.id))

        self.assertEqual(DeferredMessage.objects.count(), 0)
