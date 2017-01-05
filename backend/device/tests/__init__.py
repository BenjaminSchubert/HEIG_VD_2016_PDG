import uuid
from unittest.mock import patch

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
        self.patcher_send_fcm_message = patch("device.models.send_fcm_message")
        self.patcher_send_fcm_bulk_message = patch("device.models.send_fcm_bulk_message")
        self.mocked_send_fcm_message = self.patcher_send_fcm_message.start()
        self.mocked_send_fcm_bulk_message = self.patcher_send_fcm_bulk_message.start()

    def tearDown(self):
        self.patcher_send_fcm_message.stop()
        self.patcher_send_fcm_bulk_message.stop()
        super().tearDown()
