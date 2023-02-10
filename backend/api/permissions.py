from rest_framework import permissions


class IsAdminModeratorOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'You do not have sufficient rights to complete this request.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )
