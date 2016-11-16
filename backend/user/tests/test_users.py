from rest_framework import status

from user.models import User
from user.tests import authenticated, APIEndpointTestCase, API_V1

HTTP_METHODS = ["DELETE", "GET", "PATCH", "POST", "PUT"]


class UsersEndpointTestCase(APIEndpointTestCase):
    format = "json"
    url = API_V1 + "users/"
    correct_user = dict(username="goatsy", email="goatsy@goat.com", password="goat")

    @staticmethod
    def create_objects(number):
        for i in range(number):
            User.objects.create_user(
                email="email-{}@test.com".format(i),
                password=None,
                phone_number="+41{:09d}".format(i),
                username="user-{}".format(chr(97 + i)),
            )

    # Post Operations on /
    # this allows the creation of users

    def test_creating_user_requires_username(self):
        self.assert400WithError(self.post(dict()), "username")

    def test_creating_user_requires_password(self):
        self.assert400WithError(self.post(dict()), "password")

    def test_creating_user_requires_email(self):
        self.assert400WithError(self.post(dict()), "email")

    def test_can_create_user_while_unauthenticated(self):
        self.assertEqual(self.post(self.correct_user).status_code, status.HTTP_201_CREATED)

    def test_created_user_does_not_leak_password(self):
        self.assertNotContains(self.post(self.correct_user), "password", status.HTTP_201_CREATED)

    def test_created_user_has_hashed_password(self):
        self.assertEqual(self.post(self.correct_user).status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(User.objects.get(username="goatsy").password, self.correct_user["password"])

    def test_create_user_does_not_leak_phone_number(self):
        self.assertNotContains(self.post(self.correct_user), "phone_number", status.HTTP_201_CREATED)

    def test_cannot_create_already_existing_user(self):
        self.assertEqual(self.post(self.correct_user).status_code, status.HTTP_201_CREATED)
        self.assertContains(self.post(self.correct_user), "already exists", status_code=status.HTTP_400_BAD_REQUEST)

    def test_can_login_after_creation(self):
        self.assertEqual(self.post(self.correct_user).status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.client.login(
            email=self.correct_user["email"], password=self.correct_user["password"]
        ))
        self.client.logout()

    @authenticated
    def test_cannot_create_user_while_authenticated(self):
        self.assertEqual(self.post(dict()).status_code, status.HTTP_403_FORBIDDEN)

    # Get operations on /
    # These should returns list of users
    # we can search them using query parameters

    def test_cannot_access_users_without_authentication(self):
        self.assertEqual(self.get().status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_can_access_user_with_authentication(self):
        self.assertEqual(self.get().status_code, status.HTTP_200_OK)

    @authenticated
    def test_cannot_query_unexpected_parameter(self):
        self.assertEqual(self.get(query_params=dict(query="test")).status_code, status.HTTP_400_BAD_REQUEST)

    @authenticated
    def test_can_get_all_users(self):  # FIXME : is this really wanted ? Should it be possible ?
        self.create_objects(9)  # we need one less as we have the default user
        self.assertEqual(len(self.get().json()), 10)

    @authenticated
    def test_can_filter_by_email(self):
        self.create_objects(50)
        self.assertEqual(len(self.get(query_params=dict(email="5")).json()), 5)

    @authenticated
    def test_can_filter_by_username(self):
        self.create_objects(26)
        self.assertEqual(len(self.get(query_params=dict(username="z")).json()), 1)

    @authenticated
    def test_can_filter_by_username_and_email(self):
        for user in [
            User(username="one", email="me@one.com", password=""),
            User(username="one", email="two@two.com", password=""),
            User(username="three", email="me@three.com", password="")
        ]:
            user.save()

        self.assertEqual(len(self.get(query_params=dict(username="one", email="me")).json()), 1)

    @authenticated
    def test_can_filter_by_phone_number(self):
        self.create_objects(10)
        self.assertEqual(len(self.get(query_params=dict(phone="+41000000001")).json()), 1)

    @authenticated
    def test_can_filter_by_multiple_phone_numbers(self):
        self.create_objects(10)
        self.assertEqual(len(self.get(query_params=dict(phone=["+41000000001", "+41000000002"])).json()), 2)
