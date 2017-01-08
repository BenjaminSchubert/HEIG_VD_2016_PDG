"""Definition of all urls for the `device` application."""

from django.conf.urls import url

from device.views import DeviceView

__author__ = "Damien Rochat <rochat.damien@gmail.com>"


urlpatterns = [
    url(r"^$", DeviceView.as_view()),
]
