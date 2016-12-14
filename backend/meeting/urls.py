"""Definition of all urls for the `meeting` application."""


from django.conf.urls import url

from meeting.views import MeetingListView


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"


urlpatterns = [
    url(r"^$", MeetingListView.as_view()),
]
