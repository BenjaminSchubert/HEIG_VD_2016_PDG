"""This module defines the routes available in the `meeting` application."""
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView, \
    CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.permissions import CanViewXorOwnMeeting, IsParticipantOwner
from meeting.models import Meeting, Place, Participant
from meeting.serializers import MeetingSerializer, WriteMeetingSerializer, PlaceSerializer, ParticipantSerializer, \
    MeetingUpdateSerializer, PositionSerializer

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


class ParticipantDetailsView(UpdateAPIView):
    """
    Allows a user to manage his participation to a meeting.

    This view require the user to be authenticated. It supports PUT/PATCH requests.

    This view supports multiple formats: JSon, XML, etc.

    An example of data, in JSon, is:

        {
            "accepted": true, (optional)
            "arrived": true, (optional)
        }
    """

    serializer_class = ParticipantSerializer
    permission_classes = (IsParticipantOwner,)

    def get_object(self):
        """
        Custom get_object.

        Lookup of the Participant object related to the current logged in user
        and the meeting id provided.

        :return: the desired Participant object
        """
        queryset = Participant.objects.filter(user_id=self.request.user.id, meeting_id=self.kwargs["pk"])
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj


class PlaceListView(ListAPIView):
    """
    Returns all places known to the registered user.

    This view requires users to be authenticated.

    This view supports multiple formats: JSon, XML, etc.

    An example of data, in JSon, is:

        [
            {
                "id": 1 (the unique id of the place)
                "longitude": 0.151,  (with a maximum precision of 0.000001)
                "latitude": 1.1132,  (with a maximum precision of 0.000001)
                "name": "HEIG-VD",   (this may be null)
            },
            ...
        ]
    """

    serializer_class = PlaceSerializer

    def get_queryset(self):
        """Get all places for the registered user."""
        return Place.objects.filter(participant__user=self.request.user)


class PlaceDetailsView(RetrieveUpdateAPIView):
    """
    Allows a user to manage the places he knows.

    This view require the user to be authenticated. It supports GET and PUT/PATCH requests.

    This view supports multiple formats: JSon, XML, etc.

    An example of data, in JSon, is:

        {
            "id": 1, (the unique id of the place)
            "longitude": 1.05, (required, with a maximum precision of 0.000001)
            "latitude": 1.004, (required, with a maximum precision of 0.000001)
            "name": "HEIG-VD", (this may be null, it is a friendly name for the place, user defined)
    """

    serializer_class = PlaceSerializer

    def get_queryset(self):
        """Get all places for the registered user."""
        return Place.objects.filter(participant__user=self.request.user)


class MeetingListView(ListCreateAPIView):
    """
    Allows a user to get his meetings and create new ones.

    This view require the user to be authenticated. It supports GET and POST requests.

    This view supports multiple formats: JSon, XML, etc.

    As the meeting can be of different sorts, the format may change. Here are the various types and differences:

        * type = "shortest":

            When the type is "shortest", then the server will compute an approximation of the shortest path between
            all participants and will use this as a meeting point. If this mode is chosen, then the `place` attribute
            will be displayed on `GET` requests, but may be null as long as the server didn't finish its computation.

        * type = "place":

            When the type is "place", then the server expects a `place` attribute on creation, which contains at least
            a `longitude` and `latitude` attributes, representing the coordinates of the place. It also accepts an
            optional `name` that has no influence on the place but allows to give a human readable name of it.

        * type = "person":

            When the type is "person", then the server expects a `on` attribute on creation, which contains the id
            of the user on which to make the meeting point. The user must be in the meeting.

    Please note that then the `type` is "shortest", the server will error if any of `on` and `place` is given.
    It will also error if `on` is given when the `type` is "place" and if `place` is given when the `type` is "person".

    GET requests:
        With GET requests, this view will return data as follow (example in JSon):

            [
                {
                    "end_time": "2016-12-14T19:32:13.792217Z",  (this is the time at which the meeting ended.
                                                                  if this is null, then the meeting is still going on)

                    "id": 1,  (this is the unique id of the meeting)

                    "meeting_time": "2016-12-14T19:25:13.792217Z", (this is the time at which the meeting is planned.
                                                                    This may be null)

                    "organiser": 1, (this is the unique id of the organiser of the meeting)

                    "participants": [  (this is a list of participants, please note that the participants must be friend
                                        with the organiser)

                        {
                            "accepted": null,  (this defines whether the user accepted the meeting or not. When null,
                                                then no answer has been given yet)
                            "arrived": False,  (whether the user already arrived to the meeting point)
                            "user": 11,  (the user id)
                        },
                        ...
                    ],
                    "place": {
                        "id": 1, (the unique id of the place to which to go)
                        "latitude": 0.61,  (the latitude at which the meeting is set)
                        "longitude": 0.6,  (the longitude at which the meeting is set)
                        "name": "HEIG-VD", (the user given name of the place, optional)
                    },
                    "start_time": "2016-12-14T19:32:13.792217Z",  (this is the time at which the meeting was created)
                    "type": "shortest",  (the meeting point type, described before)
                },
                ...
            ]

    POST requests:
        With POST requests, the expected format is, for example in JSon:

            {
                "meeting_time": None,  (optional, meeting time, will default to now)
                "participants": [1,2,4],  (id of people invited to the meeting, the current user can be added or not,
                                            this does not matter.)
                "place": {
                    "latitude": 1.500024,  (required, latitude coordinate, at 0.000001 precision level)
                    "longitude": 1.50003,  (required, longitude coordinate, at 0.000001 precision level)
                    "name": "HEIG",  (optional)
                },
                "type": "place",  (the meeting point type, describe before)
            }

    Please note that all dates must be given in UTC ISO full format.
    """

    def get_queryset(self):
        """No filter."""
        return Meeting.objects

    def list(self, request, *args, **kwargs):
        """
        List of meetings where the user is participant.

        :param request: the HTTP request done
        :return a 400 or 201 response depending on whether the data was correct or not.
        """
        self.serializer_class = MeetingSerializer
        return ListCreateAPIView.list(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new meeting.

        :param request: the HTTP request done
        :return a 400 or 201 response depending on whether the data was correct or not.
        """
        self.serializer_class = WriteMeetingSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = MeetingSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MeetingDetailsView(RetrieveUpdateAPIView):
    """
    Allows a user to view and to manage meetings he created.

    This view require the user to be authenticated. It supports GET and PUT/PATCH requests.

    The user can only edit de status of the meeting. He can close or cancel it, but never set it has pending.
    He close or canceled meeting can't be altered.

    This view supports multiple formats: JSon, XML, etc.

    GET requests:
        An example of data, in JSon, is (same payload has the POST requests):

            {
                "end_time": "2016-12-14T19:32:13.792217Z",  (this is the time at which the meeting ended.
                                                              if this is null, then the meeting is still going on)

                "id": 1,  (this is the unique id of the meeting)

                "meeting_time": "2016-12-14T19:25:13.792217Z", (this is the time at which the meeting is planned.
                                                                This may be null)

                "organiser": 1, (this is the unique id of the organiser of the meeting)

                "participants": [  (this is a list of participants, please note that the participants must be friend
                                    with the organiser)

                    {
                        "accepted": null,  (this defines whether the user accepted the meeting or not. When null,
                                            then no answer has been given yet)
                        "arrived": False,  (whether the user already arrived to the meeting point)
                        "user": 11,  (the user id)
                    },
                    ...
                ],
                "place": {
                    "id": 1, (the unique id of the place to which to go)
                    "latitude": 0.61,  (the latitude at which the meeting is set)
                    "longitude": 0.6,  (the longitude at which the meeting is set)
                    "name": "HEIG-VD", (the user given name of the place, optional)
                },
                "start_time": "2016-12-14T19:32:13.792217Z",  (this is the time at which the meeting was created)
                "type": "shortest",  (the meeting point type, described before)
            }

    PUT/PATCH requests:
        An example of data, in JSon, is:

            {
                "status": "ended", (options: pending, progress, ended)
            }
    """

    permission_classes = (CanViewXorOwnMeeting,)

    def get_queryset(self):
        """No filter."""
        return Meeting.objects

    def retrieve(self, *args, **kwargs):
        """
        Override API retrieve method.

        Add custom serializer for meeting details.
        """
        self.serializer_class = MeetingSerializer
        return RetrieveUpdateAPIView.retrieve(self, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Override API update method.

        Add custom serializer for meeting updates.
        """
        self.serializer_class = MeetingUpdateSerializer
        return RetrieveUpdateAPIView.update(self, request, *args, **kwargs)


class PositionsView(CreateAPIView):
    """
    Allow to post a new position, related to the current logged in user.

    The given position will be send to all the others participants.

    This view requires the user to be authenticated.

    This view supports multiple formats : JSon, XML, etc.

    POST requests:

        The view expects the following parameters (example in JSon):

            {
                "latitude": 0.61,
                "longitude": 0.6,
            }

        - On success will return a 201 CREATED.
        - On error will send a 400, 401 depending on the error, with a message explaining it.
    """

    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        Post a new position.

        It will send the position to the participants of each meetings in progress,
        where the user is active.

        :param request: the HTTP request done
        :return a 400 or 201 response depending on whether the data was correct or not.
        """
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():

            for meeting in Meeting.objects\
                    .filter(Q(participant__user_id=self.request.user) & Q(status=Meeting.STATUS_PROGRESS))\
                    .all():

                participants = get_user_model().objects\
                    .filter(Q(participant__meeting_id=meeting.id) & Q(participant__accepted=True))

                participant = participants.get(id=self.request.user.id)
                other_participants = participants.filter(~Q(id=self.request.user.id)).all()

                other_participants.send_message(
                    title="New position",
                    body="{} position changed".format(participant.username),
                    data=dict(type="user-position-update", meeting=meeting.id, participant=participant.id),
                    deferred=False,
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
