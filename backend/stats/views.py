"""This module contains views to get statistics about the application."""


from decimal import Decimal
from django.db.models import Count, FloatField
from django.db.models import ExpressionWrapper
from django.db.models import F
from django.db.models.functions import TruncDay
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from meeting.models import Meeting, Participant
from stats.models import UserActiveInMonth
from user.models import User


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


meeting_per_users = ExpressionWrapper(
    Count("id", distinct=True) * Decimal("1.0") / Count("user", distinct=True),
    output_field=FloatField()
)


class StatisticsView(APIView):
    """
    This view allows users to get statistics about the application.

    This view requires user to be an administrator to get access to it.

    This view only supports GET requests.

    It will return a 200 OK if the user has the right, with the payload described below.
    It will return a 403 FORBIDDEN if the user is not administrator.

    This view supports multiple formats: JSon, XML, etc.

    An example response would be :
        {
            new_users: [
                {
                    day: 2017-01-01T00:00:00Z (an ECMA-262 formatted date),
                    number: 10 (number of users joined this day),
                },
                ...
            ],
            meetings_per_user: [
                {
                    day: 2017-01-01T00:00:00Z (an ECMA-262 formatted date),
                    number: 10 (number of meetings done per user having oined a meeting at this date),
                },
                ...
            ],
            active_users_per_month: [
                {
                    month: 2017-01-01T00:00:00Z (an ECMA-262 formatted date), set at the first day of the month,
                    number: 10 (number of new users during the month),
                },
                ...
            ],
            total_users: 10 (total number of users registered),
            total_meetings: 130 (total number of meetings done),
        }
    """

    permission_classes = (IsAdminUser,)

    def get(self, *args, **kwargs):
        """Get all statistics for the application."""
        return Response(dict(
            new_users=User.objects
                          .annotate(day=TruncDay("joined"))
                          .values("day")
                          .annotate(number=Count("id"))
                          .all(),
            meetings_per_user=Participant.objects
                                         .annotate(day=TruncDay(F("meeting__meeting_time")))
                                         .values("day")
                                         .annotate(number=meeting_per_users)
                                         .all(),
            active_users_per_month=UserActiveInMonth.objects
                                                    .annotate(number=F("users"))
                                                    .annotate(day=F("month"))
                                                    .values("day", "number")
                                                    .all(),
            total_users=User.objects.count(),
            total_meetings=Meeting.objects.count(),
        ))
