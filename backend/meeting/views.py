from rest_framework.generics import ListCreateAPIView

from meeting.models import Meeting
from meeting.serializers import MeetingSerializer


class MeetingListView(ListCreateAPIView):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        return Meeting.objects.all()
