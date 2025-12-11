"""
Tests for the chats app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.user_id is not None)

    def test_user_str(self):
        """Test user string representation."""
        expected = f"{self.user.first_name} {self.user.last_name} ({self.user.email})"
        self.assertEqual(str(self.user), expected)


class ConversationModelTest(TestCase):
    """Test cases for Conversation model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_creation(self):
        """Test conversation creation."""
        self.assertTrue(self.conversation.conversation_id is not None)
        self.assertEqual(self.conversation.participants.count(), 2)

    def test_conversation_participants(self):
        """Test conversation participants."""
        self.assertIn(self.user1, self.conversation.participants.all())
        self.assertIn(self.user2, self.conversation.participants.all())


class MessageModelTest(TestCase):
    """Test cases for Message model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='sender@example.com',
            password='testpass123',
            first_name='Sender',
            last_name='User'
        )
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user)
        self.message = Message.objects.create(
            sender=self.user,
            conversation=self.conversation,
            message_body='Test message'
        )

    def test_message_creation(self):
        """Test message creation."""
        self.assertTrue(self.message.message_id is not None)
        self.assertEqual(self.message.sender, self.user)
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.message_body, 'Test message')

    def test_message_str(self):
        """Test message string representation."""
        self.assertIn(self.user.first_name, str(self.message))
        self.assertIn(str(self.conversation.conversation_id), str(self.message))

