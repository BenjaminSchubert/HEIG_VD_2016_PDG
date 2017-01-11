from datetime import timedelta
from django.utils import timezone

from meeting.models import Meeting, Participant
from test_utils import APIEndpointTestCase, API_V1, authenticated


class TestMeetingPerUsers(APIEndpointTestCase):
    number_of_other_users = 15
    url = API_V1 + "statistics/"
    key = "meetings_per_user"

    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.save()

    def _create_meeting(self, meeting_time, user_ids):
        meeting = Meeting(organiser_id=1)
        meeting.save()
        meeting.start_time = meeting_time
        meeting.save()
        
        for _id in user_ids:
            Participant(meeting=meeting, user_id=_id).save()

        return meeting_time.strftime("%Y-%m-%dT00:00:00Z")

    def _check(self, value):
        self.assertListEqual(value, self.get().json()[self.key])

    @authenticated
    def test_one_meeting_two_participants(self):
        day = self._create_meeting(timezone.now(), [1, 2])
        self._check([dict(day=day, number=1.0)])

    @authenticated
    def test_two_meeting_one_participants(self):
        day = self._create_meeting(timezone.now(), [1])
        self._create_meeting(timezone.now(), [1])
        self._check([dict(day=day, number=2.0)])

    @authenticated
    def test_two_meetings_two_participants(self):
        day = self._create_meeting(timezone.now(), [1, 2])
        self._create_meeting(timezone.now(), [1, 2])
        self._check([dict(day=day, number=2.0)])

    @authenticated
    def test_two_meetings_different_days_one_participant(self):
        day1 = timezone.now()
        day2 = day1 + timedelta(days=1)
        day1 = self._create_meeting(day1, [1])
        day2 = self._create_meeting(day2, [1])

        self._check([dict(day=day1, number=1.0), dict(day=day2, number=1)])

    @authenticated
    def test_many(self):
        day1 = timezone.now()
        day2 = day1 + timedelta(days=1)
        day3 = day1 + timedelta(days=60)

        self._create_meeting(day1, [1, 2, 3, 4, 5, 6, 7])
        day1 = self._create_meeting(day1, [1, 2, 3, 4, 9])

        day2 = self._create_meeting(day2, [1, 6, 12, 13])
        day3 = self._create_meeting(day3, [11, 15, 10])

        self._check([dict(day=day1, number=1.5), dict(day=day2, number=1), dict(day=day3, number=1)])
