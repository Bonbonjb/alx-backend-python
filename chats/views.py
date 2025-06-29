from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer
from .permissions import IsParticipantOfConversation

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation_id = self.request.data.get("conversation")
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if self.request.user not in conversation.participants.all():
                return Response({"detail": "Forbidden"},
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save(sender=self.request.user)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)
