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
        self.assertEqual(thread.participants.count(), 2)
        participants = thread.participants.all()
        self.assertIn(self.user1, participants)
        self.assertIn(self.user2, participants)
        self.assertIsNotNone(thread.created)
        self.assertIsNotNone(thread.updated)

    def test_cannot_add_more_than_two_participants(self):
        thread = Thread.objects.create()
        thread.participants.add(self.user1, self.user2)

        with self.assertRaisesMessage(
            ValidationError, "A thread should have not more than 2 participants."
        ):
            thread.participants.add(self.user3)

    def test_cannot_set_more_than_two_participants_at_once(self):
        thread = Thread.objects.create()
        with self.assertRaisesMessage(
            ValidationError, "A thread should have not more than 2 participants."
        ):
            thread.participants.set([self.user1, self.user2, self.user3])


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
        self.assertIsNotNone(message.created)
        self.assertEqual(self.thread.messages.count(), 1)
        self.assertEqual(self.thread.messages.first(), message)

    def test_cannot_create_message_with_non_participant_sender(self):
        user3 = User.objects.create_user(username="user3", password="testpass123")
        with self.assertRaises(ValidationError):
            Message.objects.create(
                sender=user3, thread=self.thread, text="Invalid sender"
            )

    def test_update_message_is_read(self):
        message = Message.objects.create(
            sender=self.user1, thread=self.thread, text="Test"
        )
        message.is_read = True
        message.save()
        self.assertTrue(Message.objects.get(id=message.id).is_read)

    def test_messages_deleted_when_sender_deleted(self):
        # Create a couple messages from user1
        message1 = Message.objects.create(
            sender=self.user1, thread=self.thread, text="Message 1"
        )
        message2 = Message.objects.create(
            sender=self.user1, thread=self.thread, text="Message 2"
        )
        # Create a message from user2, to ensure, that it won't be deleted
        message3 = Message.objects.create(
            sender=self.user2, thread=self.thread, text="Message 3"
        )

        # Check messages count at the start
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(self.thread.messages.count(), 3)

        # Delete user1
        self.user1.delete()

        # Check, does the messages from user1 has been deleted, but from user2 didn't
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(self.thread.messages.count(), 1)
        self.assertEqual(self.thread.messages.first(), message3)

    def test_messages_deleted_when_thread_deleted(self):
        # Create a couple messages in a thread
        message1 = Message.objects.create(
            sender=self.user1, thread=self.thread, text="Message 1"
        )
        message2 = Message.objects.create(
            sender=self.user2, thread=self.thread, text="Message 2"
        )

        # Check messages count at the start
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(self.thread.messages.count(), 2)

        # Delete the thread
        self.thread.delete()

        # Check, does all messages has been deleted
        self.assertEqual(Message.objects.count(), 0)
