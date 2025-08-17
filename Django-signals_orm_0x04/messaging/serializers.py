from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']

class NotificationSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
