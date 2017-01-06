"""This module contains views to get statistics about the application."""

from django.db.models import Count
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncMonth
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from meeting.models import Meeting, Participant
from user.models import User


class StatisticsView(APIView):
    """View to get statistics about the application."""

    permission_classes = (IsAdminUser,)

    def get(self, *args, **kwargs):
        """Get all statistics for the application."""
        statistics = dict(
            new_users=User.objects
                          .annotate(day=TruncDay("joined"))
                          .values("day")
                          .annotate(number=Count("id"))
                          .all(),
            meetings_per_user=Participant.objects
                                         .annotate(month=TruncMonth("meeting__meeting_time"))
                                         .all(),

            total_users=User.objects.count(),
            total_meetings=Meeting.objects.count(),
        )

        return Response(statistics)
