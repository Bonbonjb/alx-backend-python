from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
     def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return request.user in obj.participants.all()
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                return request.user in obj.participants.all()
        return False

class IsOwnerOrParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user in obj.participants.all()
