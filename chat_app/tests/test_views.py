from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from chat_app.models import Thread


class ThreadViewSetTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.user3 = User.objects.create_user(username="user3", password="testpass123")

        self.client.force_authenticate(user=self.user1)
        self.url = reverse("create_thread")

    def test_create_thread_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Thread.objects.count(), 0)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_create_thread_ok(self):
        response = self.client.post(
            self.url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thread.objects.count(), 1)

    def test_create_thread_already_exists(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user1, self.user2])
        response = self.client.post(
            self.url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(response.data["id"], thread.id)

    def test_create_thread_participants(self):
        response = self.client.post(
            self.url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        thread = Thread.objects.first()
        participants = thread.participants.all()
        self.assertEqual(participants.count(), 2)
        self.assertIn(self.user1, participants)
        self.assertIn(self.user2, participants)

    def test_create_thread_invalid_data(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("This field is required.", response.data["username"][0])

    def test_create_thread_with_non_existent_user(self):
        response = self.client.post(
            self.url, {"username": "non_existent"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "User with username 'non_existent' not found.", response.data["username"][0]
        )

    def test_create_thread_with_yourself(self):
        response = self.client.post(
            self.url, {"username": self.user1.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Cannot create a thread with yourself.", response.data["username"][0]
        )
