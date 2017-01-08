"""Definition of all urls for the `statistics` application."""


from django.conf.urls import url

from stats.views import StatisticsView


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"

urlpatterns = [
    url(r"^$", StatisticsView.as_view()),
]
