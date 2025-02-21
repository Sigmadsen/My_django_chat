from django.contrib.auth.models import User
from django.test import TransactionTestCase, RequestFactory
from chat_app.models import Thread
from chat_app.serializers import UserSerializer, ThreadSerializer


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
        self.assertEqual(existing_thread.id, thread.id)
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
