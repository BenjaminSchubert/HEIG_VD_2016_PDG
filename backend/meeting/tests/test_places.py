from rest_framework import status

from meeting.models import Place, Participant, Meeting
from test_utils import APIEndpointTestCase, API_V1, authenticated


class TestMeeting(APIEndpointTestCase):
    url = API_V1 + "meetings/places/"

    def setUp(self):
        super().setUp()
        self.longitude = 0.171
        self.latitude = 0.155

        meeting = Meeting(organiser=self.user)
        meeting.save()
        place = Place(latitude=self.latitude, longitude=self.longitude)
        place.save()

        Participant(meeting=meeting, place=place, user=self.user).save()

    def test_cannot_access_places_when_unauthenticated(self):
        self.assertEqual(self.get().status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_retrieve_own_places(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(float(response.json()[0]["latitude"]), self.latitude)
        self.assertEqual(float(response.json()[0]["longitude"]), self.longitude)

    @authenticated
    def test_cannot_get_other_places(self):
        Place(latitude=0, longitude=0).save()
        self.assertEqual(len(self.get().json()), 1)

    @authenticated
    def test_can_update_own_place(self):
        response = self.put(
            dict(latitude=self.latitude + 1, longitude=self.longitude, name="HEIG"),
            url=self.url + "1/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "HEIG")

    @authenticated
    def test_cannot_update_other_place(self):
        place = Place(latitude=1, longitude=0)
        place.save()

        response = self.put(
            dict(latitude=self.latitude + 1, longitude=self.longitude),
            url=self.url + "{}/".format(place.id)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
