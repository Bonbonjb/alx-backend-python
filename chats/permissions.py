from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to view, send, update or delete messages.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For safe methods, allow if participant
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()

        # For unsafe methods: PUT, PATCH, DELETE
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user in obj.conversation.participants.all()

        return False
