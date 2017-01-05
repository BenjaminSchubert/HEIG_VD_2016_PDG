from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device, MockFcmMessagesMixin

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class BulkMessagesTestCase(MockFcmMessagesMixin, TestCase):

    def setUp(self):
        super().setUp()

        for i in range(4):
            user = get_user_model().objects.create_user(
                username="user-{}".format(i),
                email="email-{}@test.com".format(i),
            )
            create_device(user)

        self.mocked_send_fcm_message.reset_mock()

    def test_send_bulk_message(self):
        Device.objects.all().send_message()

        self.assertEqual(self.mocked_send_fcm_bulk_message.call_count, 1)

    def test_successful_message_keep_devices_as_active(self,):
        self.mocked_send_fcm_bulk_message.return_value = [dict(results=[dict(), dict(), dict(error="error"), dict()])]
        Device.objects.all().send_message()

        self.assertEqual(Device.objects.filter(is_active=True).count(), 3)

    def test_failed_message_set_devices_as_inactive(self,):
        self.mocked_send_fcm_bulk_message.return_value = [dict(results=[dict(), dict(), dict(error="error"), dict()])]
        Device.objects.all().send_message()

        self.assertEqual(Device.objects.filter(id=3, is_active=False).count(), 1)

    def test_failed_message_add_deferred_message(self):
        self.mocked_send_fcm_bulk_message.return_value = [dict(results=[dict(), dict(), dict(error="error"), dict()])]
        Device.objects.all().send_message()

        self.assertEqual(DeferredMessage.objects.count(), 1)
