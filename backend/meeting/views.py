from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from meeting.models import Meeting
from meeting.serializers import MeetingSerializer, WriteMeetingSerializer


class MeetingListView(ListCreateAPIView):
    serializer_class = WriteMeetingSerializer

    def get_queryset(self):
        return Meeting.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = MeetingSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
