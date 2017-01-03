from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.user = get_user_model().objects.create_user(username="user", email="u@tdd.com")
        self.device = create_device(self.user)

    @patch("device.models.send_fcm_message")
    def test_send_message(self, mocked_handler):
        self.device.send_message()

        self.assertEqual(mocked_handler.call_count, 1)

    @patch("device.models.send_fcm_message")
    def test_successful_message_keep_device_as_active(self, mocked_handler):
        mocked_handler.return_value = dict(success=1)
        self.device.send_message()

        self.assertTrue(Device.objects.get(id=self.device.id).is_active)

    @patch("device.models.send_fcm_message")
    def test_failed_message_set_device_as_inactive(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.device.send_message()

        self.assertFalse(Device.objects.get(id=self.device.id).is_active)

    @patch("device.models.send_fcm_message")
    def test_successful_message_do_not_add_deferred_message(self, mocked_handler):
        mocked_handler.return_value = dict(success=1)
        self.device.send_message()

        self.assertEqual(DeferredMessage.objects.count(), 0)

    @patch("device.models.send_fcm_message")
    def test_failed_message_add_deferred_message(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.device.send_message()

        self.assertEqual(DeferredMessage.objects.count(), 1)

    @patch("device.models.send_fcm_message")
    def test_send_to_inactive_do_not_try_to_send_but_add_deferred(self, mocked_handler):
        Device.objects.filter(id=self.device.id).update(is_active=False)
        self.device.refresh_from_db()

        self.device.send_message()

        self.assertEqual(mocked_handler.call_count, 0)
        self.assertEqual(DeferredMessage.objects.count(), 1)
