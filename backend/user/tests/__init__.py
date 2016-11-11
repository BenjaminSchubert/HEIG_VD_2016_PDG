import os
from PIL import Image
from abc import abstractmethod
from django.core.files import File
from functools import wraps
from io import BytesIO
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import User

API_V1 = "/v1/"


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


def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
    """
    Creates and returns an image file.

    :param name: name of the file to create
    :param ext: extension the file will have
    :param size: size of the file
    :param color: color of the image
    :return: a File object with the file
    """
    file_obj = BytesIO()
    image = Image.new("RGBA", size=size, color=color)
    image.save(file_obj, ext)
    file_obj.seek(0)
    return File(file_obj, name=name)


class APIEndpointTestCase(APITestCase):
    user = None
    password = "goat"

    @property
    @abstractmethod
    def format(self):
        """This is the format in which to send the data."""

    @property
    @abstractmethod
    def url(self):
        """This is the base url for the endpoint."""

    def setUp(self):
        """This is a base user for tests requiring authentication."""
        self.user = User.objects.create_user(username="tdd", email="goat@tdd.com", password=self.password)

    def assert400WithError(self, response, error):
        self.assertContains(response, error, status_code=status.HTTP_400_BAD_REQUEST)

    def request(self, call, url, format, *args, **kwargs):
        if url is None:
            url = self.url

        if format is None:
            format = self.format

        return call(url, format=format, *args, **kwargs)

    def post(self, data, url=None, format=None):
        return self.request(self.client.post, url, format, data)

    def get(self, url=None, format=None, query_params=None):
        return self.request(self.client.get, url, format, query_params)

    def put(self, data, url=None, format=None):
        return self.request(self.client.put, url, format, data)
