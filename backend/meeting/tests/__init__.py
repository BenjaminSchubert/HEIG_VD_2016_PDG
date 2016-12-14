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
