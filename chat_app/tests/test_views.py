from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from chat_app.models import Thread, Message


class ThreadViewSetTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.user3 = User.objects.create_user(username="user3", password="testpass123")

        self.client.force_authenticate(user=self.user1)
        self.threads_url = reverse("threads")

    def test_create_thread_status_unauthorized(self):
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

    def test_create_thread_status_created(self):
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
        self.assertEqual(set(thread_ids), {thread1.id, thread2.id})


class ThreadMessageViewSetTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.user3 = User.objects.create_user(username="user3", password="testpass123")

        self.thread_between_1_and_2 = Thread.objects.create()
        self.thread_between_1_and_2.participants.set([self.user1, self.user2])

        self.thread_between_2_and_3 = Thread.objects.create()
        self.thread_between_2_and_3.participants.set([self.user2, self.user3])

        self.client.force_authenticate(user=self.user1)

        self.messages_url = reverse("messages", args=[self.thread_between_1_and_2.id])

        self.valid_request_data = {"text": "Test message123123123"}
        self.no_field_request_data = {}
        self.empty_text_request_data = {"text": ""}
        self.none_text_request_data = {"text": None}

    def test_create_thread_message_status_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.messages_url, self.valid_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Message.objects.count(), 0)
        self.assertEqual(
            "Authentication credentials were not provided.",
            response.data["detail"],
        )

    def test_create_thread_message_status_created(self):
        response = self.client.post(
            self.messages_url, self.valid_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

    def test_create_thread_message_no_field_data(self):
        response = self.client.post(
            self.messages_url, self.no_field_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)
        self.assertEqual("This field is required.", response.data["text"][0])

    def test_create_thread_message_empty_text_data(self):
        response = self.client.post(
            self.messages_url, self.empty_text_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)
        self.assertEqual("This field may not be blank.", response.data["text"][0])

    def test_create_thread_message_none_text_data(self):
        response = self.client.post(
            self.messages_url, self.none_text_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)
        self.assertEqual("This field may not be null.", response.data["text"][0])

    def test_create_thread_message_thread_does_not_exits(self):
        non_existent_messages_url = reverse("messages", args=[100])
        response = self.client.post(
            non_existent_messages_url, self.valid_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("Thread with id 100 does not exist.", response.data["detail"])

    def test_create_thread_message_not_in_your_thread(self):
        another_thread_messages_url = reverse(
            "messages", args=[self.thread_between_2_and_3.id]
        )

        response = self.client.post(
            another_thread_messages_url, self.valid_request_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(
            "Sender must be a participant of the thread.", response.data["detail"][0]
        )

    def test_get_created_thread_messages(self):
        self.client.post(self.messages_url, self.valid_request_data, format="json")
        self.client.post(self.messages_url, self.valid_request_data, format="json")

        response = self.client.get(self.messages_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(len(response.data["results"]), 2)
        for message in response.data["results"]:
            self.assertEqual(message["text"], self.valid_request_data["text"])
            self.assertEqual(message["sender"]["id"], self.user1.id)
            self.assertFalse(message["is_read"])

        self.assertNotEqual(
            response.data["results"][0]["id"], response.data["results"][1]["id"]
        )

    def test_mark_thread_message_as_read(self):
        message = Message.objects.create(
            text="Test message123123123",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
        )
        patch_url = reverse(
            "messages", args=[self.thread_between_1_and_2.pk, message.pk]
        )
        response = self.client.patch(patch_url, {"is_read": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_try_to_patch_other_fields_from_api_for_mark_thread_message_as_read(self):
        message = Message.objects.create(
            text="Test message123123123",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
        )
        patch_url = reverse(
            "messages", args=[self.thread_between_1_and_2.pk, message.pk]
        )
        response = self.client.patch(
            patch_url, {"is_read": True, "text": "My new text", "sender": self.user3}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn(
            "Only the 'is_read' field can be updated via PATCH.",
            response.data["detail"],
        )

    def test_mark_own_thread_message_as_read(self):
        message = Message.objects.create(
            text="Test message123123123",
            sender=self.user1,
            thread=self.thread_between_1_and_2,
        )
        patch_url = reverse(
            "messages", args=[self.thread_between_1_and_2.pk, message.pk]
        )
        response = self.client.patch(patch_url, {"is_read": True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_read", response.data)
        self.assertIn(
            "You cannot mark your own message as read.", response.data["is_read"]
        )

    def test_mark_thread_message_as_not_read(self):
        message = Message.objects.create(
            text="Test message123123123",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
        )
        patch_url = reverse(
            "messages", args=[self.thread_between_1_and_2.pk, message.pk]
        )
        response = self.client.patch(patch_url, {"is_read": False})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_read", response.data)
        self.assertIn(
            "Mark a message as not read are not allowed.", response.data["is_read"]
        )

    def test_mark_thread_message_for_non_thread_participant_as_read(self):
        message = Message.objects.create(
            text="Test message123123123",
            sender=self.user3,
            thread=self.thread_between_2_and_3,
        )
        patch_url = reverse(
            "messages", args=[self.thread_between_2_and_3.pk, message.pk]
        )
        response = self.client.patch(patch_url, {"is_read": True})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual("No Message matches the given query.", response.data["detail"])

    def test_unread_count(self):
        Message.objects.create(
            text="Message 1",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
            is_read=False,
        )
        Message.objects.create(
            text="Message 2",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
            is_read=False,
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse("unread_count", args=[self.thread_between_1_and_2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unread_count"], 2)

    def test_unread_count_non_participant(self):
        Message.objects.create(
            text="Message 1",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
            is_read=False,
        )
        Message.objects.create(
            text="Message 2",
            sender=self.user2,
            thread=self.thread_between_1_and_2,
            is_read=False,
        )

        self.client.force_authenticate(user=self.user3)
        url = reverse("unread_count", args=[self.thread_between_1_and_2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            "You are not a participant of this thread or the thread does not exist.",
            response.data["detail"],
        )
