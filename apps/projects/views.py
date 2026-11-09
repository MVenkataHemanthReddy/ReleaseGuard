from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Project, Environment, ProjectToken
from .serializers import ProjectSerializer, EnvironmentSerializer, ProjectTokenSerializer
from .permissions import HasProjectAccess, IsProjectMember
from apps.core.permissions import CanManageProjects


class ProjectListCreateView(generics.ListCreateAPIView):
    """List projects for the authenticated user or create a new project."""
    serializer_class = ProjectSerializer
    permission_classes = [HasProjectAccess, CanManageProjects]

    def get_queryset(self):
        user = self.request.user
        if not user:
            return Project.objects.none()

        # Session authentication - User object
        if hasattr(user, 'is_authenticated') and not hasattr(user, '_project_token'):
            if user.is_superuser:
                return Project.objects.filter(is_active=True).select_related('organisation')
            
            # Return projects where user has membership
            return Project.objects.filter(
                organisation__memberships__user=user,
                organisation__memberships__is_active=True,
                is_active=True
            ).select_related('organisation').distinct()

        # ProjectToken authentication - Project object
        if hasattr(user, 'is_authenticated') and hasattr(user, '_project_token'):
            # Return only the project associated with the token
            return Project.objects.filter(pk=user.pk, is_active=True).select_related('organisation')

        return Project.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [CanManageProjects()]
        return [HasProjectAccess()]

    def perform_create(self, serializer):
        user = self.request.user
        # For token auth, the organisation comes from the token's project
        if hasattr(user, '_project_token'):
            organisation = user._project_token.project.organisation
        else:
            # For session auth, get the first organisation the user manages
            from apps.organizations.models import Organisation, Membership
            membership = Membership.objects.filter(
                user=user, is_active=True, organisation__is_active=True
            ).filter(role__in=['OWNER', 'ADMIN']).first()
            if not membership:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No organisation found to create project in")
            organisation = membership.organisation
        
        serializer.save(organisation=organisation)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a single project."""
    serializer_class = ProjectSerializer
    permission_classes = [HasProjectAccess, IsProjectMember]
    queryset = Project.objects.filter(is_active=True).select_related('organisation')
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageProjects()]
        return [HasProjectAccess(), IsProjectMember()]


class EnvironmentListCreateView(generics.ListCreateAPIView):
    """List environments for a project or create a new environment."""
    serializer_class = EnvironmentSerializer
    permission_classes = [HasProjectAccess, IsProjectMember]

    def get_project(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return None
        from django.shortcuts import get_object_or_404
        from .models import Project
        project = get_object_or_404(Project, pk=project_id)
        
        # Check membership
        user = self.request.user
        if hasattr(user, 'is_superuser'):  # Session auth - User object
            if not user.is_superuser:
                has_access = user.memberships.filter(
                    organisation=project.organisation,
                    is_active=True,
                    organisation__is_active=True,
                ).exists()
                if not has_access:
                    self.permission_denied(self.request, message='Not a member of this project\'s organisation')
        elif hasattr(user, 'is_authenticated') and user.is_authenticated:  # ProjectToken auth - Project object
            if user.pk != project.pk:
                self.permission_denied(self.request, message='Token not valid for this project')
        else:
            self.permission_denied(self.request, message='Authentication required')
        
        return project

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return Environment.objects.none()
        return Environment.objects.filter(project=project, is_active=True)

    def perform_create(self, serializer):
        project = self.get_project()
        if project:
            serializer.save(project=project)


class EnvironmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a single environment."""
    serializer_class = EnvironmentSerializer
    permission_classes = [HasProjectAccess, IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return Environment.objects.none()
        return Environment.objects.filter(project=project, is_active=True)

    def get_project(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return None
        from django.shortcuts import get_object_or_404
        from .models import Project
        project = get_object_or_404(Project, pk=project_id)
        
        user = self.request.user
        if hasattr(user, 'is_superuser'):  # Session auth
            if not user.is_superuser:
                has_access = user.memberships.filter(
                    organisation=project.organisation,
                    is_active=True,
                    organisation__is_active=True,
                ).exists()
                if not has_access:
                    self.permission_denied(self.request, message='Not a member of this project\'s organisation')
        elif hasattr(user, 'is_authenticated') and user.is_authenticated:  # Token auth
            if user.pk != project.pk:
                self.permission_denied(self.request, message='Token not valid for this project')
        else:
            self.permission_denied(self.request, message='Authentication required')
        
        return project

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [HasProjectAccess(), IsProjectMember()]
        return [HasProjectAccess(), IsProjectMember()]


class ProjectTokenCreateView(generics.CreateAPIView):
    """Create a new project token for CI/CD authentication."""
    serializer_class = ProjectTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_project(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return None
        from django.shortcuts import get_object_or_404
        from .models import Project
        project = get_object_or_404(Project, pk=project_id)
        
        user = self.request.user
        if hasattr(user, 'is_superuser'):  # Session auth
            if not user.is_superuser:
                has_access = user.memberships.filter(
                    organisation=project.organisation,
                    is_active=True,
                    organisation__is_active=True,
                ).exists()
                if not has_access:
                    self.permission_denied(self.request, message='Not a member of this project\'s organisation')
        elif hasattr(user, 'is_authenticated') and user.is_authenticated:  # Token auth
            if user.pk != project.pk:
                self.permission_denied(self.request, message='Token not valid for this project')
        else:
            self.permission_denied(self.request, message='Authentication required')
        
        return project

    def perform_create(self, serializer):
        project = self.get_project()
        if project:
            serializer.save(project=project)