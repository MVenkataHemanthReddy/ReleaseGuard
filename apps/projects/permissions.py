"""
Custom permissions for ReleaseGuard.
"""
from rest_framework import permissions


class HasProjectAccess(permissions.BasePermission):
    """
    Check if the request has valid project access.

    Works with both session authentication (User) and
    ProjectToken authentication (Project).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user:
            return False

        # Session authentication - User object
        if hasattr(user, 'is_authenticated'):
            return user.is_authenticated

        # ProjectToken authentication - Project object with is_authenticated flag
        if hasattr(user, 'is_authenticated') and user.is_authenticated:
            return True

        return False


class IsProjectMember(permissions.BasePermission):
    """
    Check if the user is a member of the project's organisation.
    """

    def has_permission(self, request, view):
        return HasProjectAccess().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user:
            return False

        # Session authentication - check membership
        if hasattr(user, 'is_authenticated') and not hasattr(user, '_project_token'):
            if user.is_superuser:
                return True
            return obj.organisation.memberships.filter(
                user=user,
                is_active=True
            ).exists()

        # ProjectToken authentication - the project IS the object
        if hasattr(user, 'is_authenticated') and user.is_authenticated:
            return obj.pk == user.pk

        return False