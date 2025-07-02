from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

class IsOwnerOrParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user in obj.participants.all()
       