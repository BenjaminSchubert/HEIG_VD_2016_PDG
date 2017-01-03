from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeferredMessagesTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.user = get_user_model().objects.create_user(username="user", email="u@tdd.com")
        self.device = create_device(self.user)

    @patch("device.models.send_fcm_message")
    def test_successful_deferred_message_remove_it_from_db(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.device.send_message("Message title", "Message body", "test-message")

        mocked_handler.return_value = dict(success=1)
        Device.objects.filter(id=self.device.id).update(is_active=True)
        self.device.send_deferred_message(DeferredMessage.objects.last())

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 0)

    @patch("device.models.send_fcm_message")
    def test_failed_deferred_message_update_it_in_db(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.device.send_message("Message title", "Message body", "test-message")

        self.device.send_deferred_message(DeferredMessage.objects.last())

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 1)
