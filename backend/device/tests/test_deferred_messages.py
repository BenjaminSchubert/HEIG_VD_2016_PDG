from django.contrib.auth import get_user_model
from django.test import TestCase

from device.models import DeferredMessage, Device
from device.tests import create_device, MockFcmMessagesMixin

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


class DeferredMessagesTestCase(MockFcmMessagesMixin, TestCase):

    def setUp(self):
        super().setUp()

        self.user = get_user_model().objects.create_user(username="user", email="u@tdd.com")
        self.device = create_device(self.user)

        self.mocked_send_fcm_message.reset_mock()

    def test_deferred_message_is_saved(self):
        DeferredMessage(user=self.user, title="title", body="body", data=dict(type="test-message", id=1)).save()

        message = DeferredMessage.objects.last()
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.title, "title")
        self.assertEqual(message.body, "body")
        self.assertDictEqual(message.data, dict(type="test-message", id=1))

    def test_successful_deferred_message_remove_it_from_db(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)
        self.device.send_message(title="title", body="body")

        self.mocked_send_fcm_message.return_value = dict(success=1)
        Device.objects.filter(id=self.device.id).update(is_active=True)
        self.device.send_deferred_message(DeferredMessage.objects.last())

        self.assertEqual(DeferredMessage.objects.filter(user=self.user).count(), 0)

    def test_failed_deferred_message_update_it_in_db(self):
        self.mocked_send_fcm_message.return_value = dict(success=0)
        self.device.send_message(title="title", body="body")

        self.device.send_deferred_message(DeferredMessage.objects.last())

        self.assertEqual(DeferredMessage.objects.filter(user=self.user).count(), 1)
