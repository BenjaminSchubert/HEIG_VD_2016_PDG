"""Definition of all urls for the `user` application."""


from django.conf.urls import url

from user.views import UsersListView, UserProfileView, UserAvatarView, FriendListView, FriendListDetailsView, \
    AllFriendListView, BlockedFriendListView, PendingFriendListView, HiddenPendingFriendListView

__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"


urlpatterns = [
    url(r"^$", UsersListView.as_view()),
    url(r"^me/$", UserProfileView.as_view()),
    url(r"^me/avatar/$", UserAvatarView.as_view()),
    url(r"^friends/$", FriendListView.as_view()),
    url(r"^friends/all/$", AllFriendListView.as_view()),
    url(r"^friends/blocked/$", BlockedFriendListView.as_view()),
    url(r"^friends/hidden/$", HiddenPendingFriendListView.as_view()),
    url(r"^friends/pending/$", PendingFriendListView.as_view()),
    url(r"^friends/(?P<pk>[0-9]+)/$", FriendListDetailsView.as_view()),
]
