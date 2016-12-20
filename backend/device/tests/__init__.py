import uuid

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
