from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Organisation, Membership
from .serializers import OrganisationSerializer


def get_user_organisation_queryset(user):
    """Get organisations for a user (handles both User and Project auth)."""
    # Session authentication - User object
    if hasattr(user, 'is_superuser') and not hasattr(user, '_project_token'):
        if user.is_superuser:
            return Organisation.objects.filter(is_active=True)
        return Organisation.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            is_active=True
        ).distinct()
    
    # ProjectToken authentication - Project object
    if hasattr(user, 'is_authenticated') and hasattr(user, '_project_token'):
        # Return the organisation of the project
        return Organisation.objects.filter(
            pk=user.organisation.pk,
            is_active=True
        )
    
    return Organisation.objects.none()


class OrganisationListCreateView(generics.ListCreateAPIView):
    """List organisations for the authenticated user or create a new organisation."""
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_user_organisation_queryset(self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        
        # Create organisation and make the creator an owner
        organisation = serializer.save()
        
        # Only create membership for session auth (User objects)
        if hasattr(user, 'is_superuser') and not hasattr(user, '_project_token'):
            Membership.objects.create(
                user=user,
                organisation=organisation,
                role=Membership.Role.OWNER,
                is_active=True
            )
        # For token auth, the user is a Project, not a User, so no membership needed
        
        return organisation


class OrganisationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a single organisation."""
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return get_user_organisation_queryset(self.request.user)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only owners/admins can modify/delete - check in object permission
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        
        # Check permissions based on auth type
        if hasattr(user, 'is_superuser') and not hasattr(user, '_project_token'):
            # Session auth - check membership
            if not user.is_superuser:
                has_access = user.memberships.filter(
                    organisation=obj,
                    is_active=True,
                    organisation__is_active=True
                ).exists()
                if not has_access:
                    raise PermissionDenied('You do not have access to this organisation.')
        elif hasattr(user, 'is_authenticated') and hasattr(user, '_project_token'):
            # Token auth - check project's organisation matches
            if user.organisation.pk != obj.pk:
                raise PermissionDenied('Token not valid for this organisation.')
        
        return obj