from rest_framework import filters
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter
from .pagination import MessagePagination

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_pk") or self.request.query_params.get("conversation_id")
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        # Check permission
        self.check_object_permissions(self.request, conversation)
        return Message.objects.filter(conversation=conversation).order_by("sent_at")

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation_id")
        conversation = get_object_or_404(Conversation, pk=conversation_id)

        # Check permission
        self.check_object_permissions(self.request, conversation)

        serializer.save(sender=self.request.user, conversation=conversation)
