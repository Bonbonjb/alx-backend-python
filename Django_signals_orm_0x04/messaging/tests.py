from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessageSignalTest(TestCase):
    def test_notification_created_on_message(self):
        sender = User.objects.create_user(username='alice')
        receiver = User.objects.create_user(username='bob')

        message = Message.objects.create(sender=sender, receiver=receiver, content="Hello Bob!")

        notification = Notification.objects.filter(user=receiver, message=message)
        self.assertTrue(notification.exists())