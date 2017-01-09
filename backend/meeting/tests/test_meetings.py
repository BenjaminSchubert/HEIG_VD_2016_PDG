from unittest import expectedFailure

from django.contrib.auth import get_user_model
from rest_framework import status

from device.models import DeferredMessage
from device.tests import MockFcmMessagesMixin
from meeting.models import Meeting, Participant
from meeting.tests import create_meeting
from test_utils import APIEndpointTestCase, API_V1, authenticated
from user.models import Friendship


class TestMeeting(APIEndpointTestCase):
    url = API_V1 + "meetings/"
    number_of_other_users = 10

    def test_cannot_create_meeting_when_unauthenticated(self):
        self.assertEqual(self.post(dict()).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_cannot_create_new_meeting_with_invalid_type(self):
        self.assert400WithError(self.post(dict(type="hello")), "choice")

    @authenticated
    def test_cannot_create_new_meeting_on_place_without_place(self):
        self.assert400WithError(self.post(dict(type="place")), "required")

    @authenticated
    def test_cannot_create_new_meeting_on_place_with_wrong_place(self):
        response = self.post(dict(type="place", place=dict()))
        self.assert400WithError(response, "longitude")
        self.assert400WithError(response, "latitude")

    @authenticated
    def test_cannot_create_new_meeting_on_place_with_misformed_place(self):
        response = self.post(dict(type="place", place=dict(latitude="h", longitude="b")))
        self.assert400WithError(response, "longitude")
        self.assert400WithError(response, "latitude")

    @authenticated
    def test_participants_is_required(self):
        self.assert400WithError(self.post(dict()), "participants")

    @authenticated
    def test_at_least_one_participant_is_required(self):
        self.assert400WithError(self.post(dict(participants=[], type="place")), "one participant")

    @authenticated
    def test_at_least_one_participant_plus_organizer_is_required(self):
        self.assert400WithError(self.post(dict(participants=[self.user.id], type="place")), "one participant")

    @authenticated
    def test_cannot_add_user_that_is_not_friend(self):
        self.assert400WithError(
            self.post(dict(
                participants=[get_user_model().objects.last().id],
                type="place",
                place=dict(latitude=0, longitude=1))
            ),
            "friends"
        )

    @authenticated
    def test_cannot_add_user_that_did_not_accept_friend_request(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend).save()

        self.assert400WithError(
            self.post(dict(
                type="place",
                place=dict(latitude=0, longitude=1),
                participants=[friend.id]
            )),
            "friends"
        )

    @authenticated
    def test_cannot_add_user_from_which_friend_request_was_not_accepted(self):
        friend = get_user_model().objects.last()
        Friendship(to_account=self.user, from_account=friend).save()

        self.assert400WithError(
            self.post(dict(
                type="place",
                place=dict(latitude=0, longitude=1),
                participants=[friend.id]
            )),
            "friends"
        )

    @authenticated
    def test_cannot_add_user_that_is_inactive(self):
        friend = get_user_model().objects.last()
        friend.is_active = False
        friend.save()

        friendships = [
            Friendship(to_account=self.user, from_account=friend, is_accepted=True),
            Friendship(from_account=self.user, to_account=friend, is_accepted=True)
        ]

        for friendship in friendships:
            friendship.save()

            self.assert400WithError(
                self.post(dict(
                    type="place",
                    place=dict(latitude=0, longitude=1),
                    participants=[friend.id]
                )),
                "friends"
            )

            friendship.delete()

    @authenticated
    def test_can_create_new_meeting_on_place(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.assertEqual(
            self.post(dict(type="place", place=dict(latitude=0, longitude=1), participants=[friend.id])).status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(Meeting.objects.first().status, Meeting.STATUS_PROGRESS)

    @authenticated
    def test_can_create_new_meeting_on_person(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.assertEqual(
            self.post(dict(type="person", participants=[friend.id])).status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(Meeting.objects.first().status, Meeting.STATUS_PENDING)

    @expectedFailure
    @authenticated
    def test_can_create_new_meeting_on_shortest_path(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.assertEqual(
            self.post(dict(type="shortest", participants=[friend.id])).status_code,
            status.HTTP_201_CREATED
        )

    @expectedFailure
    @authenticated
    def test_cannot_get_others_meetings(self):
        Meeting(organiser=get_user_model().objects.last()).save()
        self.assertEqual(len(self.get().json()), 0)

    @authenticated
    def test_can_get_own_meetings(self):
        meeting = Meeting(organiser=self.user)
        meeting.save()

        Participant(meeting=meeting, user=self.user).save()
        self.assertEqual(len(self.get().json()), 1)

    @authenticated
    def test_can_get_meeting_in_which_we_participate(self):
        meeting = Meeting(organiser=get_user_model().objects.last())
        meeting.save()

        Participant(meeting=meeting, user=self.user).save()
        self.assertEqual(len(self.get().json()), 1)

    @authenticated
    def test_organiser_accepted_meeting(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.post(dict(type="place", place=dict(latitude=0, longitude=1), participants=[friend.id]))

        self.assertTrue(Participant.objects.get(user=self.user).accepted)

    @authenticated
    def test_no_organiser_not_accepted_meeting(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.post(dict(type="place", place=dict(latitude=0, longitude=1), participants=[friend.id]))

        self.assertFalse(Participant.objects.get(user=friend).accepted)

    @authenticated
    def test_hidden_user_auto_refuse_meetings(self):
        friend = get_user_model().objects.last()
        friend.hidden = True
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.post(dict(type="place", place=dict(latitude=0, longitude=1), participants=[friend.id]))
        self.assertFalse(Participant.objects.get(user=friend).accepted)


class TestMeetingDetails(MockFcmMessagesMixin, APIEndpointTestCase):
    url = API_V1 + "meetings/{}/"
    number_of_other_users = 1

    def test_cannot_retrieve_meetings_details_when_unauthenticated(self):
        meeting = create_meeting(self.user)

        self.assertEqual(self.get(url=self.url.format(meeting.id)).status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_retrieve_own_meetings_details(self):
        meeting = create_meeting(self.user)

        self.assertEqual(self.get(url=self.url.format(meeting.id)).status_code, status.HTTP_200_OK)

    @authenticated
    def test_cannot_retrieve_others_meetings_details(self):
        meeting = Meeting(organiser=get_user_model().objects.exclude(id=self.user.id).first())
        meeting.save()

        self.assertEqual(self.get(url=self.url.format(meeting.id)).status_code, status.HTTP_403_FORBIDDEN)

    @authenticated
    def test_organiser_can_set_meeting_status_has_progress(self):
        meeting = create_meeting(self.user)

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_PROGRESS), url=self.url.format(meeting.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_PROGRESS)

    @authenticated
    def test_organiser_can_set_meeting_status_has_ended(self):
        meeting = create_meeting(self.user)

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_ENDED), url=self.url.format(meeting.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_ENDED)

    @authenticated
    def test_organiser_can_set_meeting_status_has_canceled(self):
        meeting = create_meeting(self.user)

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_CANCELED), url=self.url.format(meeting.id)).status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_CANCELED)

    @authenticated
    def test_only_organiser_can_update_meeting(self):
        meeting = create_meeting(get_user_model().objects.exclude(id=self.user.id).first())

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_ENDED), url=self.url.format(meeting.id)).status_code,
            status.HTTP_403_FORBIDDEN
        )

    @authenticated
    def test_cannot_update_ended_meeting(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_ENDED
        meeting.save(update_fields=("status",))

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_PROGRESS), url=self.url.format(meeting.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_ENDED)

    @authenticated
    def test_cannot_update_canceled_meeting(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_CANCELED
        meeting.save(update_fields=("status",))

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_ENDED), url=self.url.format(meeting.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_CANCELED)

    @authenticated
    def test_cannot_set_meeting_has_pending(self):
        meeting = create_meeting(self.user)

        meeting.status = Meeting.STATUS_PROGRESS
        meeting.save(update_fields=("status",))

        self.assertEqual(
            self.put(dict(status=Meeting.STATUS_PENDING), url=self.url.format(meeting.id)).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Meeting.objects.get(id=meeting.id).status, Meeting.STATUS_PROGRESS)

    @authenticated
    def test_ended_meeting_cancel_related_deferred_messages(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)

        meeting = create_meeting(self.user)

        self.put(dict(status=Meeting.STATUS_ENDED), url=self.url.format(meeting.id))

        self.assertEqual(DeferredMessage.objects.count(), 0)

    @authenticated
    def test_canceled_meeting_cancel_related_deferred_messages(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)

        meeting = create_meeting(self.user)

        self.put(dict(status=Meeting.STATUS_CANCELED), url=self.url.format(meeting.id))

        self.assertEqual(DeferredMessage.objects.count(), 0)
