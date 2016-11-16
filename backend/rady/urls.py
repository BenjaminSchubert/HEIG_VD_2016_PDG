"""Defines all Rady URL."""


from django.conf.urls import url, include
from django.contrib import admin

from auth import urls as auth_urls


apiv1_urls = [
    url(r"^users/", include("user.urls")),
    url(r"^docs/", include("rest_framework_docs.urls")),
    url(r'^auth/', include(auth_urls)),
    url(r"^auth/", include(auth_urls)),
]

urlpatterns = [
    url(r"^v1/", include(apiv1_urls)),
    url(r'^admin/', admin.site.urls),
    url(r"^admin/", admin.site.urls),
]
