from abc import abstractmethod
from django.contrib.auth import get_user_model
from functools import wraps
from rest_framework import status
from rest_framework.test import APITestCase


API_V1 = "/api/v1/"


def authenticated(f):
    """
    Force the user to be logged in.

    This decorator must be applied on a function that has a `client` instance attached to its `self` attribute.

    :param f: function to decorate
    :return: decorated function
    """
    @wraps(f)
    def _decorator(*args, **kwargs):
        self = args[0]
        try:
            self.client.force_authenticate(user=self.user)  # authenticate
            return f(*args, **kwargs)
        except:
            self.client.force_authenticate(user=None)  # deauthenticate
            raise

    return _decorator


class APIEndpointTestCase(APITestCase):
    format = "json"
    user = None
    password = "goat"

    number_of_other_users = 0

    @property
    @abstractmethod
    def url(self):
        """This is the base url for the endpoint."""

    def setUp(self):
        """This is a base user for tests requiring authentication."""
        super().setUp()

        self.user = get_user_model().objects.create_user(username="tdd", email="goat@tdd.com", password=self.password)

        for i in range(self.number_of_other_users):
            get_user_model().objects.create_user(
                email="email-{}@test.com".format(i),
                password=None,
                phone_number="+41{:09d}".format(i),
                username="user-{}".format(chr(97 + i)),
            )

    def assert400WithError(self, response, error):
        self.assertContains(response, error, status_code=status.HTTP_400_BAD_REQUEST)

    # noinspection PyShadowingBuiltins
    def request(self, call, url, format, *args, **kwargs):
        if url is None:
            url = self.url

        if format is None:
            # noinspection PyShadowingBuiltins
            format = self.format

        return call(url, format=format, *args, **kwargs)

    # noinspection PyShadowingBuiltins
    def post(self, data, url=None, format=None):
        return self.request(self.client.post, url, format, data)

    # noinspection PyShadowingBuiltins
    def get(self, url=None, format=None, query_params=None):
        return self.request(self.client.get, url, format, query_params)

    # noinspection PyShadowingBuiltins
    def put(self, data, url=None, format=None):
        return self.request(self.client.put, url, format, data)

    # noinspection PyShadowingBuiltins
    def delete(self, url=None, format=None):
        return self.request(self.client.delete, url, format)
