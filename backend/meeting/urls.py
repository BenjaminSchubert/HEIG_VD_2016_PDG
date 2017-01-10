"""Definition of all urls for the `meeting` application."""


from django.conf.urls import url

from meeting.views import MeetingListView, PlaceListView, PlaceDetailsView, ParticipantDetailsView, \
    MeetingDetailsView,  PositionsView

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"


urlpatterns = [
    url(r"^$", MeetingListView.as_view()),
    url(r"^(?P<pk>[0-9]+)/$", MeetingDetailsView.as_view()),
    url(r"^places/$", PlaceListView.as_view()),
    url(r"^places/(?P<pk>[0-9]+)/$", PlaceDetailsView.as_view()),
    url(r"^(?P<pk>[0-9]+)/participants/$", ParticipantDetailsView.as_view()),
    url(r"^positions/$", PositionsView.as_view()),
]
