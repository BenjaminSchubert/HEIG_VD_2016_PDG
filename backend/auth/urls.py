"""Defines all `auth` application URLs."""

from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.contrib.auth import views as auth_views

from auth.views import SessionLoginView, reset_password

urlpatterns = [
    url(r'^password-reset/$', reset_password, name='password_reset'),
    url(r'^password-reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),

    url(r'^login/$', obtain_jwt_token),
    url(r"^session/$", SessionLoginView.as_view()),
    url(r'^refresh/$', refresh_jwt_token),
]
