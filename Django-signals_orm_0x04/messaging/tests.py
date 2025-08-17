import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from .models import Message, Notification

User = get_user_model()

@pytest.mark.django_db
class TestMessagingSignals(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="alice", 
            email="alice@example.com", 
            password="pass123"
        )
        self.receiver = User.objects.create_user(
            username="bob", 
            email="bob@example.com", 
            password="pass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.sender)

    def test_notification_created_on_message_creation(self):
        # Test that a notification is created when a message is sent
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )
        
        # Check that a notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_conversation_endpoint(self):
        # Create some test messages
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )
        Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Hi Alice!"
        )
        
        # Get the conversation
        url = reverse('conversation', kwargs={'user_id': self.receiver.id})
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # Should return both messages

class MessageViewSetTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", 
            email="user1@example.com", 
            password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", 
            email="user2@example.com", 
            password="pass123"
        )
        self.client.force_authenticate(user=self.user1)
    
    def test_message_creation(self):
        """Test that a message can be created through the API"""
        url = '/api/messages/'
        data = {
            'receiver_id': self.user2.id,
            'content': 'Test message'
        }
        
        # Create a message
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Verify the message was created
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Test message')
        
        # Verify a notification was created for the receiver
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
    
    def test_list_messages(self):
        """Test that a user can list their messages"""
        # Create some test messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1"
        )
        Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 2"
        )
        
        # Get messages
        url = '/api/messages/'
        response = self.client.get(url)
        
        # Should return both messages (sent and received)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], 'Message 2')
        self.assertEqual(response.data[1]['content'], 'Message 1')
