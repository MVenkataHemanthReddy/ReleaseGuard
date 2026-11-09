"""
Core permission classes for ReleaseGuard.

All permissions enforce organisation-level scoping — a UUID alone is NOT
sufficient for authorisation. Every request must be checked against the
user's membership in the relevant organisation.
"""

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsAuthenticated(permissions.IsAuthenticated):
    """
    Extends DRF's IsAuthenticated to provide clearer error messages.
    """

    message = 'Authentication credentials were not provided or are invalid.'


class IsOrganisationMember(permissions.BasePermission):
    """
    Base class for permissions that require organisation membership.

    Subclasses must implement `get_organisation(obj, request)` to return
    the organisation to check membership against.
    """

    message = 'You do not have access to this organisation.'

    def get_organisation(self, obj, request):
        """
        Return the organisation to check membership for.

        Must be implemented by subclasses.
        """
        raise NotImplementedError('Subclasses must implement get_organisation()')

    def has_permission(self, request, view):
        # Must be authenticated first
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        organisation = self.get_organisation(obj, request)
        if not organisation:
            return False

        # Check active membership in organisation
        return request.user.memberships.filter(
            organisation=organisation,
            is_active=True,
            organisation__is_active=True,
        ).exists()


class IsOrganisationOwnerOrAdmin(IsOrganisationMember):
    """
    Permission for organisation owners and admins only.
    """

    message = 'You must be an owner or admin of this organisation.'

    def has_object_permission(self, request, view, obj):
        organisation = self.get_organisation(obj, request)
        if not organisation:
            return False

        return request.user.memberships.filter(
            organisation=organisation,
            is_active=True,
            organisation__is_active=True,
            role__in=['OWNER', 'ADMIN'],
        ).exists()


class IsProjectMember(permissions.BasePermission):
    """
    Permission for users with any active role in the project's organisation.
    """

    message = 'You do not have access to this project.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # obj can be Project, Environment, Release, etc.
        project = getattr(obj, 'project', obj)
        if not hasattr(project, 'organisation'):
            return False

        return request.user.memberships.filter(
            organisation=project.organisation,
            is_active=True,
            organisation__is_active=True,
        ).exists()


class IsProjectAdmin(permissions.BasePermission):
    """
    Permission for users with OWNER, ADMIN, or MEMBER role in project's organisation.
    (VIEWER can only read)
    """

    message = 'You must have at least MEMBER role in this project\'s organisation.'

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, 'project', obj)
        if not hasattr(project, 'organisation'):
            return False

        membership = request.user.memberships.filter(
            organisation=project.organisation,
            is_active=True,
            organisation__is_active=True,
        ).first()

        if not membership:
            return False

        # Allow read for all roles
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write requires MEMBER or above
        return membership.role in ['OWNER', 'ADMIN', 'MEMBER']


class IsTokenAuthenticated(permissions.BasePermission):
    """
    Permission for project-scoped token authentication.

    Used for CI/CD ingestion endpoints. The token is verified in the
    authentication class, not here. This permission just ensures the
    request has a valid token attached.
    """

    message = 'Invalid or missing project token.'

    def has_permission(self, request, view):
        # Token authentication is handled by authentication class
        # This just checks that a token was successfully authenticated
        return hasattr(request, 'auth') and request.auth is not None


class CanManageReleases(permissions.BasePermission):
    """
    Permission to create/manage releases in a project.
    """

    message = 'You do not have permission to manage releases in this project.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, 'project', obj)
        if not hasattr(project, 'organisation'):
            return False

        membership = request.user.memberships.filter(
            organisation=project.organisation,
            is_active=True,
            organisation__is_active=True,
        ).first()

        if not membership:
            return False

        # Allow read for all roles
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write requires MEMBER or above
        return membership.role in ['OWNER', 'ADMIN', 'MEMBER']


class CanManageProjects(permissions.BasePermission):
    """
    Permission to create/manage projects in an organisation.
    """

    message = 'You do not have permission to manage projects in this organisation.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # obj can be Project or Organisation
        if hasattr(obj, 'organisation'):
            organisation = obj.organisation
        else:
            organisation = obj
        
        membership = request.user.memberships.filter(
            organisation=organisation,
            is_active=True,
            organisation__is_active=True,
        ).first()

        if not membership:
            return False

        # Allow read for all roles
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write requires ADMIN or OWNER
        return membership.role in ['OWNER', 'ADMIN']