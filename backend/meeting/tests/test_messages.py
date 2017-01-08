import random
from unittest.mock import ANY, call

from django.contrib.auth import get_user_model
from django.db.models import Q

from device.tests import create_device, MockFcmMessagesMixin
from meeting.models import Meeting, Participant
from meeting.tests import create_meeting
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
    def test_new_meeting_send_push_notifications_to_all_participants(self):
        other_participants = get_user_model().objects.exclude(id=self.user.id)  # no message to organiser

        self.post(
            dict(
                type="place",
                place=dict(latitude=0, longitude=1),
                participants=other_participants.values_list("id", flat=True)
            ),
            url=API_V1 + "meetings/"
        )

        self.assertEqual(self.mocked_send_fcm_message.call_count, other_participants.count())
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
            for u in other_participants
        ], any_order=True)

    @authenticated
    def test_accept_meeting_send_push_to_participants_who_accepted_or_are_pending(self):
        meeting = create_meeting(get_user_model().objects.exclude(id=self.user.id).first())

        my_participant = Participant.objects.get(user=self.user)
        my_participant.accepted = None
        my_participant.save(update_fields=("accepted",))

        # no message to actuator and participants who declined
        other_participants = meeting.participants\
            .exclude(Q(id=self.user.id) | Q(participant__accepted=False))\
            .all()

        self.put(dict(accepted=True), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in other_participants],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-accepted-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_refused_meeting_send_push_to_participants_who_accepted_or_are_pending(self):
        meeting = create_meeting(get_user_model().objects.exclude(id=self.user.id).first())

        my_participant = Participant.objects.get(user=self.user)
        my_participant.accepted = None
        my_participant.save(update_fields=("accepted",))

        # no message to actuator
        other_participants = meeting.participants\
            .exclude(Q(id=self.user.id) | Q(participant__accepted=False))\
            .all()

        self.put(dict(accepted=False), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in other_participants],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-refused-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_user_arrived_at_meeting_send_push_to_participants_who_accepted(self):
        meeting = create_meeting(get_user_model().objects.exclude(id=self.user.id).first())

        my_participant = Participant.objects.get(user=self.user)
        my_participant.accepted = True
        my_participant.save(update_fields=("accepted",))

        # no message to actuator
        other_participants = meeting.participants\
            .exclude(id=self.user.id)\
            .filter(participant__accepted=True)\
            .all()

        self.put(dict(arrived=True), url=API_V1 + "meetings/participants/{}/".format(my_participant.id))

        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in other_participants],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "user-arrived-to-meeting", "meeting": meeting.id, "participant": my_participant.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_progress_meeting_send_push_to_participants_who_accepted(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_PROGRESS
        meeting.save(update_fields=("status",))

        users = meeting.participants.filter(participant__accepted=True).all()
        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "meeting-in-progress", "meeting": meeting.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_ended_meeting_send_push_to_participants_who_accepted(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_ENDED
        meeting.save(update_fields=("status",))

        users = meeting.participants.filter(participant__accepted=True).all()
        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "finished-meeting", "meeting": meeting.id},
            sound=ANY,
            badge=ANY,
        )

    @authenticated
    def test_canceled_meeting_send_push_to_participants_who_accepted(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_CANCELED
        meeting.save(update_fields=("status",))

        users = meeting.participants.filter(participant__accepted=True).all()
        self.mocked_send_fcm_bulk_message.assert_called_once_with(
            registration_ids=[u.get_device().registration_id for u in users],
            message_title=ANY,
            message_body=ANY,
            message_icon=ANY,
            data_message={"type": "canceled-meeting", "meeting": meeting.id},
            sound=ANY,
            badge=ANY,
        )
