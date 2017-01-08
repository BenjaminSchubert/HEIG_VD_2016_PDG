"""Definition of all urls for the `admin` application."""

from django.conf.urls import url

from admin.views import UserListView, UserDetailsView

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"

urlpatterns = [
    url(r"^users/$", UserListView.as_view()),
    url(r"^users/(?P<pk>[0-9]+)/$", UserDetailsView.as_view())
]
