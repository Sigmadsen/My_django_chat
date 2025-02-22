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
        self.threads_url = reverse("threads")

    def test_create_thread_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.threads_url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Thread.objects.count(), 0)
        self.assertEqual(
            "Authentication credentials were not provided.",
            response.data["detail"],
        )

    def test_create_thread_ok(self):
        response = self.client.post(
            self.threads_url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thread.objects.count(), 1)

    def test_create_thread_already_exists(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user1, self.user2])
        response = self.client.post(
            self.threads_url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(response.data["id"], thread.id)

    def test_create_thread_participants(self):
        response = self.client.post(
            self.threads_url, {"username": self.user2.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        thread = Thread.objects.first()
        participants = thread.participants.all()
        self.assertEqual(participants.count(), 2)
        self.assertIn(self.user1, participants)
        self.assertIn(self.user2, participants)

    def test_create_thread_invalid_data(self):
        response = self.client.post(self.threads_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertEqual("This field is required.", response.data["username"][0])

    def test_create_thread_with_non_existent_user(self):
        response = self.client.post(
            self.threads_url, {"username": "non_existent"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "User with username 'non_existent' not found.", response.data["username"][0]
        )

    def test_create_thread_with_yourself(self):
        response = self.client.post(
            self.threads_url, {"username": self.user1.username}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "Cannot create a thread with yourself.", response.data["username"][0]
        )

    def test_delete_thread_success(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user1, self.user2])
        delete_url = reverse("delete_thread", args=[thread.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Thread.objects.filter(id=thread.id).exists())

    def thread_does_not_exist(self):
        delete_url = reverse("delete_thread", args=[1])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            "No Thread matches the given query.",
            response.data["detail"],
        )

    def test_delete_thread_not_participant(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user2, self.user3])

        delete_url = reverse("delete_thread", args=[thread.id])
        response = self.client.delete(delete_url)
        # We can't found other people's thread because have set up get_queryset() method with request.user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("No Thread matches the given query.", response.data["detail"])

    def test_list_threads(self):
        thread1 = Thread.objects.create()
        thread1.participants.set([self.user1, self.user2])

        thread2 = Thread.objects.create()
        thread2.participants.set([self.user1, self.user3])

        # Thread without user 1 that logged in - this user should not see a thread between user2 and user3
        thread3 = Thread.objects.create()
        thread3.participants.set([self.user2, self.user3])

        response = self.client.get(self.threads_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        thread_ids = [thread["id"] for thread in response.data["results"]]
        self.assertEqual(thread_ids, [thread1.id, thread2.id])
