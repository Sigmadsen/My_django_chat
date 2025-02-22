from django.contrib.auth.models import User
from django.test import TransactionTestCase, RequestFactory
from chat_app.models import Thread
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

        self.thread = Thread.objects.create()
        self.thread.participants.set([self.user1, self.user2])

        self.valid_request_data = {"text": "Test message123123123"}
        self.no_field_request_data = {}
        self.empty_text_request_data = {"text": ""}
        self.none_text_request_data = {"text": None}

    def test_create_valid_message(self):
        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"sender": self.user1, "thread_id": self.thread.id},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        message = serializer.save()

        self.assertEqual(message.text, self.valid_request_data["text"])
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.thread, self.thread)

    def test_create_message_no_fields(self):
        serializer = ThreadMessageSerializer(
            data=self.no_field_request_data,
            context={"sender": self.user1, "thread_id": self.thread.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field is required.", str(serializer.errors["text"]))

    def test_create_message_empty_text(self):
        serializer = ThreadMessageSerializer(
            data=self.empty_text_request_data,
            context={"sender": self.user1, "thread_id": self.thread.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field may not be blank.", str(serializer.errors["text"]))

    def test_create_message_null_text(self):
        serializer = ThreadMessageSerializer(
            data=self.none_text_request_data,
            context={"sender": self.user1, "thread_id": self.thread.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)
        self.assertIn("This field may not be null.", str(serializer.errors["text"]))

    def test_create_message_non_existing_thread(self):
        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"sender": self.user1, "thread_id": 100},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "Thread with id 100 does not exist.", str(serializer.errors["detail"])
        )

    def test_create_message_not_your_thread(self):
        serializer = ThreadMessageSerializer(
            data=self.valid_request_data,
            context={"sender": self.user3, "thread_id": self.thread.id},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "Sender must be a participant of the thread.",
            str(serializer.errors["detail"]),
        )
