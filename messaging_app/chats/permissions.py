from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own data.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
