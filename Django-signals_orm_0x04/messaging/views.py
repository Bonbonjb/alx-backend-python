from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Message, Notification
from .serializers import MessageSerializer, NotificationSerializer

User = get_user_model()

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)

    def perform_create(self, serializer):
        # Extract receiver_id from the request data
        receiver_id = self.request.data.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)
        serializer.save(sender=self.request.user, receiver=receiver)

    @action(detail=False, methods=['get'])
    def conversation(self, request, user_id=None):
        other_user = get_object_or_404(User, id=user_id)
        messages = Message.objects.filter(
            sender=request.user, receiver=other_user
        ) | Message.objects.filter(
            sender=other_user, receiver=request.user
        ).order_by('timestamp')
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_read=False)

    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

def delete_user(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return Response({'status': 'user deleted'}, status=status.HTTP_204_NO_CONTENT)
    return Response({'error': 'Invalid method'}, status=status.HTTP_400_BAD_REQUEST)
