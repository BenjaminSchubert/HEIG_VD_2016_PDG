from unittest import expectedFailure

from django.contrib.auth import get_user_model
from rest_framework import status

from meeting.models import Meeting, Participant
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

    @expectedFailure
    @authenticated
    def test_can_create_new_meeting_on_person(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.assertEqual(
            self.post(dict(type="on", participants=[friend.id])).status_code,
            status.HTTP_201_CREATED
        )

    @expectedFailure
    @authenticated
    def test_can_create_new_meeting_on_shortest_path(self):
        friend = get_user_model().objects.last()
        Friendship(from_account=self.user, to_account=friend, is_accepted=True).save()

        self.assertEqual(
            self.post(dict(type="shortest", participants=[friend.id])).status_code,
            status.HTTP_201_CREATED
        )

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
