from django.contrib.auth import get_user_model
from rest_framework import status

from test_utils import APIEndpointTestCase, API_V1, authenticated


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
        print(self.post(dict()).json())
        self.assert400WithError(self.post(dict()), "participants")

    @authenticated
    def test_at_least_one_participant_is_required(self):
        print(self.post(dict(participants=[], type="place")).json())
        self.assert400WithError(self.post(dict(participants=[], type="place")), "one participant")

    @authenticated
    def test_at_least_one_participant_plus_organizer_is_required(self):
        self.assert400WithError(self.post(dict(participants=[self.user.id], type="place")), "one participant")
