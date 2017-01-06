import uuid
from unittest.mock import patch

import pyfcm

from device.models import Device


def generate_device_info():
    return dict(
        registration_id=uuid.uuid4()
    )


def create_device(user):
    info = generate_device_info()
    info["user"] = user
    device = Device(**info)
    device.save()
    return device


class MockFcmMessagesMixin:

    def setUp(self):
        super().setUp()

        # prevent initialisation of the FCMNotification module who try to get the FCM token
        self.patcher_fcmnotification_init = patch.object(pyfcm.FCMNotification, "__init__", return_value=None).start()
        self.patcher_fcmnotification_init.return_value = None

        self.patcher_send_fcm_message = patch.object(pyfcm.FCMNotification, "notify_single_device")
        self.patcher_send_fcm_bulk_message = patch.object(pyfcm.FCMNotification, "notify_multiple_devices")
        self.mocked_send_fcm_message = self.patcher_send_fcm_message.start()
        self.mocked_send_fcm_bulk_message = self.patcher_send_fcm_bulk_message.start()

    def tearDown(self):
        self.patcher_send_fcm_message.stop()
        self.patcher_send_fcm_bulk_message.stop()

        self.patcher_fcmnotification_init.stop()

        super().tearDown()
