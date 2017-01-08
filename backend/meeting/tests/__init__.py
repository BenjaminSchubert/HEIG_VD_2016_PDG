from django.contrib.auth import get_user_model

from meeting.models import Meeting, Participant


class TestCaseWithUsersMixin:
    def setUp(self):
        super().setUp()
        for i in range(5):
            User.objects.create_user(
                email="email-{}@test.com".format(i),
                password=None,
                phone_number="+41{:09d}".format(i),
                username="user-{}".format(chr(97 + i)),
            )


def create_meeting(organiser):
    meeting = Meeting(organiser=organiser)
    meeting.save()
    Participant(meeting=meeting, user=organiser, accepted=True).save()
    choices = [True, False, None]
    for i, user in enumerate(get_user_model().objects.exclude(id=organiser.id).all()):
        Participant(meeting=meeting, user=user, accepted=choices[i % 3]).save()
    return meeting
