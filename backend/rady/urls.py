"""Defines all Rady URL."""


from django.conf.urls import url
from django.contrib import admin

from auth import urls as auth_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/auth/', include(auth_urls)),
]
