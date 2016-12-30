from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeferredMessagesTestCase(TestCase):

    def setUp(self):
        super(DeferredMessagesTestCase, self).setUp()

        self.user = get_user_model().objects.create_user(username="user1", email="u1@tdd.com")
        create_device(self.user)

    @patch("user.models.send_fcm_message")
    def test_successful_message_set_device_as_active(self, mocked_handler):
        mocked_handler.return_value = dict(success=1)
        self.user.send_message(title="Message title", body="Message body", type="test-message")

        self.assertTrue(Device.objects.get(id=self.user.get_device().id).is_active)

    @patch("user.models.send_fcm_message")
    def test_failed_message_set_device_as_inactive(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message(title="Message title", body="Message body", type="test-message")

        self.assertFalse(Device.objects.get(id=self.user.get_device().id).is_active)

    @patch("user.models.send_fcm_message")
    def test_successful_message_do_not_add_deferred_message(self, mocked_handler):
        mocked_handler.return_value = dict(success=1)
        self.user.send_message("Message title", "Message body", "test-message")

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 0)

    @patch("user.models.send_fcm_message")
    def test_failed_message_add_deferred_message(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message("Message title", "Message body", "test-message")

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 1)

    @patch("user.models.send_fcm_message")
    def test_send_to_inactive_do_not_try_to_send_but_add_deferred(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message("Message title", "Message body", "test-message")  # Device is now set as inactive
        self.user.send_message("Message title", "Message body", "test-message")

        self.assertEqual(mocked_handler.call_count, 1)
        self.assertEqual(DeferredMessage.objects.filter(user=self.user).count(), 2)

    @patch("user.models.send_fcm_message")
    def test_try_to_send_deferred_messages_on_device_registration(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message("Message title", "Message body", "test-message")
        self.user.send_message("Message title", "Message body", "test-message")

        mocked_handler.reset_mock()
        mocked_handler.return_value = dict(success=1)
        create_device(self.user)

        self.assertEqual(mocked_handler.call_count, 2)

    @patch("user.models.send_fcm_message")
    def test_successful_deferred_message_remove_it_from_db(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message("Message title", "Message body", "test-message")

        mocked_handler.return_value = dict(success=1)
        create_device(self.user)

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 0)

    @patch("user.models.send_fcm_message")
    def test_failed_deferred_message_update_it_in_db(self, mocked_handler):
        mocked_handler.return_value = dict(success=0)
        self.user.send_message("Message title", "Message body", "test-message")
        create_device(self.user)

        self.assertEqual(DeferredMessage.objects.filter(user=self.user, type="test-message").count(), 1)
