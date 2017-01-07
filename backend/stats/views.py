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
    """View to get statistics about the application."""

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
