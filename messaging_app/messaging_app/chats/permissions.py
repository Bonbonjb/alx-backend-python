# messaging_app/chats/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    """
    Custom permission to allow only owners to access their data.
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods like GET are allowed if the user is the owner
        return obj.user == request.user
