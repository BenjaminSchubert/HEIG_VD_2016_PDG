from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device, MockFcmMessagesMixin

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class MessagesTestCase(MockFcmMessagesMixin, TestCase):

    def setUp(self):
        super().setUp()

        self.user = get_user_model().objects.create_user(username="user", email="u@tdd.com")
        self.device = create_device(self.user)

        self.mocked_send_fcm_message.reset_mock()

    def test_send_message(self):
        self.device.send_message()

        self.assertEqual(self.mocked_send_fcm_message.call_count, 1)

    def test_successful_message_keep_device_as_active(self):
        self.mocked_send_fcm_message.return_value = dict(success=1)
        self.device.send_message()

        self.assertTrue(Device.objects.get(id=self.device.id).is_active)

    def test_failed_message_set_device_as_inactive(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)
        self.device.send_message()

        self.assertFalse(Device.objects.get(id=self.device.id).is_active)

    def test_successful_message_do_not_add_deferred_message(self):
        self.mocked_send_fcm_message.return_value = dict(success=1)
        self.device.send_message()

        self.assertEqual(DeferredMessage.objects.count(), 0)

    def test_failed_message_add_deferred_message(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)
        self.device.send_message()

        self.assertEqual(DeferredMessage.objects.count(), 1)

    def test_send_to_inactive_do_not_try_to_send_but_add_deferred(self):
        Device.objects.filter(id=self.device.id).update(is_active=False)
        self.device.refresh_from_db()

        self.device.send_message()

        self.assertEqual(self.mocked_send_fcm_message.call_count, 0)
        self.assertEqual(DeferredMessage.objects.count(), 1)
