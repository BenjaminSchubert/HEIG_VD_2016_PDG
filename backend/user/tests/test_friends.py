from unittest.mock import patch, ANY

from django.db.models.signals import post_save
from rest_framework import status

from user.models import User, Friendship
from test_utils import APIEndpointTestCase, API_V1, authenticated


class FriendsMainEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "users/friends/"
    number_of_other_users = 10

    def test_cannot_access_friends_unauthenticated(self):
        self.assertEqual(self.get().status_code, status.HTTP_401_UNAUTHORIZED)

    @authenticated
    def test_user_has_no_friends_at_first(self):
        self.assertEqual(len(self.get().json()), 0)

    @authenticated
    def test_can_add_friend(self):
        self.assertEqual(self.post(dict(friend=2)).status_code, status.HTTP_201_CREATED)

    @authenticated
    def test_newly_added_friend_is_pending(self):
        self.assertFalse(self.post(dict(friend=2)).json()["is_accepted"])

    @authenticated
    def test_cannot_be_friend_with_self(self):
        response = self.post(dict(friend=self.user.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("friend", response.json().keys())

    @authenticated
    def test_can_see_when_blocking(self):
        Friendship(from_account=self.user, to_account=User.objects.last(), from_blocking=True).save()
        self.assertTrue(self.get(self.url + "all/").json()[0]["is_blocked"], msg="Couldn't see that user was blocked")

    @authenticated
    def test_cannot_see_when_blocked(self):
        Friendship(from_account=self.user, to_account=User.objects.last(), to_blocking=True).save()
        self.assertFalse(self.get(self.url + "all/").json()[0]["is_blocked"], msg="Could see that I was blocked")

    @authenticated
    def test_cannot_be_friend_twice_with_same_person_when_adding(self):
        Friendship(from_account=self.user, to_account=User.objects.last()).save()
        self.assertContains(
            self.post(dict(friend=User.objects.last().id)),
            "already",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_cannot_be_friend_twice_with_same_person_when_added(self):
        Friendship(from_account=User.objects.last(), to_account=self.user).save()
        self.assertContains(
            self.post(dict(friend=User.objects.last().id)),
            "already",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_can_get_only_pending_requests(self):
        users = User.objects.all()

        Friendship(from_account=users[1], to_account=self.user).save()
        Friendship(from_account=self.user, to_account=users[2]).save()
        Friendship(from_account=users[3], to_account=self.user, is_accepted=True).save()

        response = self.get(url=self.url + "pending/").json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["friend"]["username"], users[1].username)

    @authenticated
    def test_can_get_only_blocked_friends(self):
        users = User.objects.all()

        Friendship(from_account=users[1], to_account=self.user, to_blocking=True).save()
        Friendship(from_account=self.user, to_account=users[2], to_blocking=True).save()
        Friendship(from_account=users[3], to_account=self.user).save()
        Friendship(from_account=self.user, to_account=users[4], from_blocking=True).save()

        response = self.get(url=self.url + "blocked/").json()
        self.assertEqual(len(response), 2)
        self.assertListEqual([u["friend"]["username"] for u in response], [users[1].username, users[4].username])

    @authenticated
    def test_can_get_only_hidden_friends(self):
        users = User.objects.all()

        Friendship(from_account=users[1], to_account=self.user, is_hidden=True).save()
        Friendship(from_account=users[2], to_account=self.user).save()
        Friendship(from_account=self.user, to_account=users[3], is_hidden=True).save()
        Friendship(from_account=self.user, to_account=users[4]).save()

        response = self.get(url=self.url + "hidden/").json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["friend"]["username"], users[1].username)

    @authenticated
    def test_can_get_all_friends(self):
        users = User.objects.all()

        Friendship(from_account=users[1], to_account=self.user, is_hidden=True).save()
        Friendship(from_account=self.user, to_account=users[2], from_blocking=True).save()
        Friendship(from_account=users[3], to_account=self.user, from_blocking=True).save()
        Friendship(from_account=self.user, to_account=users[4], is_accepted=True).save()

        self.assertEqual(len(self.get(url=self.url + "all/").json()), 4)

    @authenticated
    def test_can_get_only_active_friends(self):
        users = User.objects.all()

        Friendship(from_account=users[1], to_account=self.user, is_hidden=True).save()
        Friendship(from_account=self.user, to_account=users[2], from_blocking=True, is_accepted=True).save()
        Friendship(from_account=users[3], to_account=self.user, from_blocking=True, is_accepted=True).save()
        Friendship(from_account=self.user, to_account=users[4], is_accepted=True).save()

        self.assertEqual(len(self.get().json()), 2)

    @authenticated
    @patch('user.signals.post_save_friendship')
    def test_new_friendship_emit_post_save_signal(self, mocked_handler):

        # Bind mocked handler to the event and emit signal
        post_save.connect(mocked_handler, sender=Friendship)
        Friendship(from_account=self.user, to_account=User.objects.last()).save()

        self.assertEquals(mocked_handler.call_count, 1)

    @authenticated
    @patch('user.signals.post_save_friendship')
    def test_update_friendship_emit_post_save_signal(self, mocked_handler):
        friendship = Friendship(from_account=self.user, to_account=User.objects.last())
        friendship.save()

        # Bind mocked handler to the event and emit signal
        post_save.connect(mocked_handler, sender=Friendship)
        friendship.is_accepted = True
        friendship.save()

        self.assertEquals(mocked_handler.call_count, 1)

    @authenticated
    @patch('fcm_django.fcm.fcm_send_message')
    def test_new_friendship_send_push_notification(self, mocked_handler):
        from .test_device import UserDeviceEndpointTestCase
        user = User.objects.last()
        UserDeviceEndpointTestCase.generate_device(user)

        Friendship(from_account=self.user, to_account=user).save()

        mocked_handler.assert_called_once_with(
            registration_id=user.get_device().registration_id,
            data={"type": "friend-request"},
            title=ANY,
            body=ANY,
            badge=ANY,
            icon=ANY,
            sound=ANY,
        )

    @authenticated
    def test_accept_friendship_send_push_notification(self):
        from .test_device import UserDeviceEndpointTestCase
        UserDeviceEndpointTestCase.generate_device(self.user)
        friendship = Friendship(from_account=self.user, to_account=User.objects.last())
        friendship.save()

        with patch('fcm_django.fcm.fcm_send_message') as mocked_handler:
            friendship.is_accepted = True
            friendship.save()

        mocked_handler.assert_called_once_with(
            registration_id=self.user.get_device().registration_id,
            data={"type": "friend-request-accepted"},
            title=ANY,
            body=ANY,
            badge=ANY,
            icon=ANY,
            sound=ANY,
        )


class FriendsDetailsEndpointTestCase(APIEndpointTestCase):
    url = API_V1 + "users/friends/{}/"
    number_of_other_users = 10

    def setUp(self):
        super().setUp()
        Friendship(from_account=self.user, to_account=User.objects.all()[2]).save()
        Friendship(from_account=User.objects.all()[3], to_account=self.user).save()

    @authenticated
    def test_can_get_specific_friendship(self):
        response = self.get(url=self.url.format(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertDictEqual(
            response.json(),
            dict(
                is_accepted=False, is_blocked=False, is_hidden=False,
                friend=dict(avatar=None, username=User.objects.all()[2].username, id=User.objects.all()[2].id)
            )
        )

    @authenticated
    def test_can_accept_friendship(self):
        self.assertEqual(self.put(dict(is_accepted=True), url=self.url.format(2)).status_code, status.HTTP_200_OK)

    @authenticated
    def test_cannot_accept_friendship_when_owner(self):
        self.assertEqual(
            self.put(dict(is_accepted=True), url=self.url.format(1)).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_cannot_block_friend_if_not_accepted(self):
        self.assertEqual(
            self.put(dict(is_blocked=True), url=self.url.format(1)).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_can_block_friend_that_added_us(self):
        friendship = Friendship.objects.last()
        friendship.is_accepted = True
        friendship.save()

        response = self.put(dict(is_blocked=True), url=self.url.format(Friendship.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["is_blocked"])

    @authenticated
    def test_can_block_friend_we_added(self):
        friendship = Friendship.objects.first()
        friendship.is_accepted = True
        friendship.save()

        response = self.put(dict(is_blocked=True), url=self.url.format(Friendship.objects.first().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["is_blocked"])

    @authenticated
    def test_can_unblock_friend(self):
        friendship = Friendship.objects.last()
        friendship.is_accepted = True
        friendship.from_blocking = True
        friendship.to_blocking = True
        friendship.save()

        response = self.put(dict(is_blocked=False), url=self.url.format(Friendship.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["is_blocked"])

    @authenticated
    def test_can_hide_pending_request(self):
        response = self.put(dict(is_hidden=True), url=self.url.format(Friendship.objects.last().id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["is_hidden"])

    @authenticated
    def test_cannot_hide_non_pending_request(self):
        friendship = Friendship.objects.last()
        friendship.is_accepted = True
        friendship.save()

        self.assertContains(
            self.put(dict(is_hidden=True), url=self.url.format(friendship.id)),
            "hide",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @authenticated
    def test_cannot_hide_own_request(self):
        response = self.put(dict(is_hidden=True), url=self.url.format(Friendship.objects.first().id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @authenticated
    def test_cannot_unaccept_previously_accepted_request(self):
        friendship = Friendship.objects.last()
        friendship.is_accepted = True
        friendship.save()

        self.assertContains(
            self.put(dict(is_accepted=False), url=self.url.format(friendship.id)),
            "un-accept",
            status_code=status.HTTP_400_BAD_REQUEST
        )
