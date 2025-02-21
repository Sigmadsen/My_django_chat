from django.test import TransactionTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from chat_app.models import (
    Thread,
    Message,
)


class ThreadModelTest(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.user3 = User.objects.create_user(username="user3", password="testpass123")

    def test_create_valid_thread(self):
        thread = Thread.objects.create()
        thread.participants.add(self.user1, self.user2)
        thread.clean()
        self.assertEqual(thread.participants.count(), 2)

    def test_thread_max_participants(self):
        thread = Thread.objects.create()
        thread.participants.add(self.user1, self.user2)

        with self.assertRaises(ValidationError):
            thread.participants.add(self.user3)
            thread.clean()


class MessageModelTest(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.thread = Thread.objects.create()
        self.thread.participants.add(self.user1, self.user2)

    def test_create_message(self):
        message = Message.objects.create(
            sender=self.user1, thread=self.thread, text="Test message"
        )

        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.thread, self.thread)
        self.assertEqual(message.text, "Test message")
        self.assertFalse(message.is_read)
