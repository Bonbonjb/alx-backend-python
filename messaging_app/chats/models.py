import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    password = models.CharField(max_length=128)  # <-- explicitly declared

    REQUIRED_FIELDS = ["email", "first_name", "last_name", "phone_number"]
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username

# Conversation model
class Conversation(models.Model):
    conversation_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    participants = models.ManyToManyField(User, related_name="user_conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"

# Message model
class Message(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="conversation_messages")
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.message_body[:20]}"
