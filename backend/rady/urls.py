"""Defines all Rady URL."""

from django.conf.urls import url, include
from django.contrib import admin


apiv1_urls = [
    url(r"^users/", include("user.urls")),
    url(r"^meetings/", include("meeting.urls")),
    url(r"^docs/", include("rest_framework_docs.urls")),
    url(r"^auth/", include("auth.urls")),
    url(r"^fcm/devices/", include("device.urls")),
    url(r"^statistics/", include("stats.urls")),
    url(r"^admin/", include("admin.urls")),
]

urlpatterns = [
    url(r"^api/v1/", include(apiv1_urls)),
    url(r"^admin/", admin.site.urls),
]
