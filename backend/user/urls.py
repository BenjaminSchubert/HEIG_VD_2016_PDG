"""Definition of all urls for the `user` application."""


from django.conf.urls import url

from user.views import UsersListView, UserProfileView, UserAvatarView


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com"


urlpatterns = [
    url(r"^$", UsersListView.as_view()),
    url(r"^me/$", UserProfileView.as_view()),
    url(r"^me/avatar/$", UserAvatarView.as_view())
]
