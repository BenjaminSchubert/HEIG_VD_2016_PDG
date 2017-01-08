"""
Utilities to send FCM messages.

Based on xtrinch/fcm-django (https://github.com/xtrinch/fcm-django)
Use lucurious/PyFCM (https://github.com/olucurious/PyFCM)
"""

from django.conf import settings
from pyfcm import FCMNotification


def send_fcm_message(registration_id,
                     title=None,
                     body=None,
                     icon=None,
                     data=None,
                     sound=None,
                     badge=None, **kwargs):
    """Send a push notification with FCM to a device."""
    api_key = settings.FCM_SETTINGS.get("FCM_SERVER_KEY")
    push_service = FCMNotification(api_key=api_key)

    return push_service.notify_single_device(registration_id=registration_id,
                                             message_title=title,
                                             message_body=body,
                                             message_icon=icon,
                                             data_message=data,
                                             sound=sound,
                                             badge=badge,
                                             **kwargs)


def send_fcm_bulk_message(registration_ids,
                          title=None,
                          body=None,
                          icon=None,
                          data=None,
                          sound=None,
                          badge=None, **kwargs):
    """Send a push notification with FCM to multiple devices."""
    api_key = settings.FCM_SETTINGS.get("FCM_SERVER_KEY")
    push_service = FCMNotification(api_key=api_key)

    return push_service.notify_multiple_devices(
        registration_ids=registration_ids,
        message_title=title,
        message_body=body,
        message_icon=icon,
        data_message=data,
        sound=sound,
        badge=badge,
        **kwargs
    )
