from django.contrib.auth.models import User
from django.test import TransactionTestCase, RequestFactory
from chat_app.models import Thread, Message
from chat_app.serializers import (
    UserSerializer,
    ThreadSerializer,
    ThreadMessageSerializer,
)


class UserSerializerTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

    def test_user_read_serializer(self):
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(serializer.data, {"id": self.user.id, "username": "testuser"})

    def test_user_serializer_many(self):
        user2 = User.objects.create_user(username="testuser2", password="password123")
        serializer = UserSerializer(instance=[self.user, user2], many=True)
        expected_data = [
            {"id": self.user.id, "username": "testuser"},
            {"id": user2.id, "username": "testuser2"},
        ]
        self.assertEqual(serializer.data, expected_data)


class ThreadSerializerTest(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.user3 = User.objects.create_user(username="user3", password="password123")

    def test_create_valid_thread(self):
        request = self.factory.post("/api/threads/")
        request.user = self.user1
        serializer = ThreadSerializer(
            data={"username": "user2"}, context={"request": request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        thread = serializer.save()
        self.assertEqual(thread.participants.count(), 2)
        participants = thread.participants.all()
        self.assertIn(self.user1, participants)
        self.assertIn(self.user2, participants)
        self.assertFalse(getattr(serializer, "_existing_thread", False))
        expected_data = {
            "id": thread.id,
            "participants": [
                {"id": self.user1.id, "username": "user1"},
                {"id": self.user2.id, "username": "user2"},
            ],
            "created": serializer.data["created"],
            "updated": serializer.data["updated"],
        }
        self.assertEqual(serializer.data, expected_data)

    def test_create_thread_with_non_existent_user(self):
        request = self.factory.post("/api/threads/")
        request.user = self.user1
        serializer = ThreadSerializer(
            data={"username": "non_existent"}, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertIn(
            "User with username 'non_existent' not found",
            str(serializer.errors["username"]),
        )

    def test_create_thread_with_yourself(self):
        request = self.factory.post("/api/threads/")
        request.user = self.user1
        serializer = ThreadSerializer(
            data={"username": "user1"}, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertIn(
            "Cannot create a thread with yourself", str(serializer.errors["username"])
        )

    def test_create_existing_thread(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user1, self.user2])

        request = self.factory.post("/api/threads/")
        request.user = self.user1
        serializer = ThreadSerializer(
            data={"username": "user2"}, context={"request": request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        existing_thread = serializer.save()

        # Check that we got the same id from serializer as we created at the start of the test
        self.assertEqual(existing_thread.id, thread.id)

        # If it is no such attribute in serializer then set it to False
        self.assertTrue(getattr(serializer, "_existing_thread", False))

        expected_data = {
            "id": thread.id,
            "participants": [
                {"id": self.user1.id, "username": "user1"},
                {"id": self.user2.id, "username": "user2"},
            ],
            "created": serializer.data["created"],
            "updated": serializer.data["updated"],
        }
        self.assertEqual(serializer.data, expected_data)

    def test_serialize_existing_thread(self):
        thread = Thread.objects.create()
        thread.participants.set([self.user1, self.user2])
        serializer = ThreadSerializer(instance=thread)
        expected_data = {
            "id": thread.id,
            "participants": [
                {"id": self.user1.id, "username": "user1"},
                {"id": self.user2.id, "username": "user2"},
            ],
            "created": serializer.data["created"],
            "updated": serializer.data["updated"],
        }
        self.assertEqual(serializer.data, expected_data)


class ThreadMessageSerializerTest(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.user3 = User.objects.create_user(username="user3", password="testpass123")

        self.thread_between_1_and_2 = Thread.objects.create()

        self.thread_between_1_and_2.participants.set([self.user1, self.user2])

        self.valid_request_data = {"text": "Test message123123123"}
        self.no_field_request_data = {}
        self.empty_text_request_data = {"text": ""}
        self.none_text_request_data = {"text": None}

        self.message = Message.objects.create(
            text="Test message123123123",
            sender=self.user1,
            thread=self.thread_between_1_and_2,
        )

    def test_create_valid_message(self):
        request = self.factory.post(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()

        self.assertEqual(message.text, self.valid_request_data["text"])
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.thread, self.thread_between_1_and_2)

    def test_create_message_with_no_fields(self):
        request = self.factory.post(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            data=self.no_field_request_data,
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field is required.", str(serializer.errors["text"]))

    def test_create_message_with_empty_text(self):
        request = self.factory.post(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            data=self.empty_text_request_data,
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field may not be blank.", str(serializer.errors["text"]))

    def test_create_message_with_null_text(self):
        request = self.factory.post(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            data=self.none_text_request_data,
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field may not be null.", str(serializer.errors["text"]))

    def test_create_message_with_non_existing_thread(self):
        request = self.factory.post("/api/threads/100/messages")
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"request": request, "thread_id": 100},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "Thread with id 100 does not exist.", str(serializer.errors["detail"])
        )

    def test_create_message_in_not_your_thread(self):
        request = self.factory.post(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user3

        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "Sender must be a participant of the thread.",
            str(serializer.errors["detail"]),
        )

    def test_mark_message_as_read(self):
        request = self.factory.patch(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user2

        serializer = ThreadMessageSerializer(
            instance=self.message,
            data={"is_read": True},
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_mark_own_message_as_read(self):
        request = self.factory.patch(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user1

        serializer = ThreadMessageSerializer(
            instance=self.message,
            data={"is_read": True},
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("is_read", serializer.errors)
        self.assertIn(
            "You cannot mark your own message as read.", serializer.errors["is_read"]
        )

    def test_mark_message_as_not_read(self):
        request = self.factory.patch(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user2
        serializer = ThreadMessageSerializer(
            instance=self.message,
            data={"is_read": False},
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("is_read", serializer.errors)
        self.assertIn(
            "Mark a message as not read are not allowed.", serializer.errors["is_read"]
        )

    def test_mark_message_of_non_thread_participant_as_read(self):
        request = self.factory.patch(
            f"/api/threads/{self.thread_between_1_and_2.id}/messages"
        )
        request.user = self.user3
        serializer = ThreadMessageSerializer(
            instance=self.message,
            data={"is_read": True},
            context={"request": request, "thread_id": self.thread_between_1_and_2.id},
            partial=True,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "Sender must be a participant of the thread.", serializer.errors["detail"]
        )
