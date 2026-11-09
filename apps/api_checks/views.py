"""
API views for API Health Checks.
"""

import logging
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.api_checks.serializers import (
    ApiCheckSerializer,
    ApiCheckCreateSerializer,
    ApiCheckResultSerializer,
    ApiCheckRunSerializer,
)
from apps.api_checks.services import ApiCheckService
from apps.projects.models import Project
from apps.core.permissions import IsProjectMember, IsProjectAdmin
from apps.core.exceptions import custom_exception_handler

logger = logging.getLogger(__name__)


class ProjectScopedViewSetMixin:
    """Mixin to scope all queries to user's projects via organisation membership."""

    def get_project(self):
        """Get project from URL kwargs, with permission check."""
        project_id = self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        if not project_id:
            return None

        project = get_object_or_404(Project, pk=project_id)

        # Check membership
        user = self.request.user
        if not user.is_superuser:
            has_access = user.memberships.filter(
                organisation=project.organisation,
                is_active=True,
                organisation__is_active=True,
            ).exists()
            if not has_access:
                self.permission_denied(self.request, message='Not a member of this project\'s organisation')

        return project


class ApiCheckViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for API Health Check management.

    Endpoints:
    - POST   /api/v1/projects/{project_pk}/api-checks/     -> Create check
    - GET    /api/v1/projects/{project_pk}/api-checks/     -> List checks
    - GET    /api/v1/projects/{project_pk}/api-checks/{pk}/ -> Check detail
    - PATCH  /api/v1/projects/{project_pk}/api-checks/{pk}/ -> Update check
    - DELETE /api/v1/projects/{project_pk}/api-checks/{pk}/ -> Delete check
    - POST   /api/v1/projects/{project_pk}/api-checks/{pk}/run/ -> Manual execution
    """

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return ApiCheck.objects.none()
        return ApiCheck.objects.filter(project=project).select_related(
            'environment'
        ).prefetch_related('results')

    def get_serializer_class(self):
        if self.action == 'create':
            return ApiCheckCreateSerializer
        if self.action == 'run':
            return ApiCheckRunSerializer
        return ApiCheckSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        """Set project on creation."""
        project = self.get_project()
        serializer.save(project=project)

    @action(detail=True, methods=['post'])
    def run(self, request, *args, **kwargs):
        """Manually trigger an API check."""
        api_check = self.get_object()

        # Validate request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        triggered_by = serializer.validated_data.get('triggered_by', 'manual')
        idempotency_key = serializer.validated_data.get('idempotency_key', '')

        # Execute check
        service = ApiCheckService(api_check)
        result = service.run_check(triggered_by=triggered_by, idempotency_key=idempotency_key)

        return Response(
            ApiCheckResultSerializer(result, context=self.get_serializer_context()).data,
            status=status.HTTP_202_ACCEPTED,
        )


class ApiCheckResultViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for API Check Result queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/api-check-results/ -> List results
    - GET /api/v1/projects/{project_pk}/api-check-results/{pk}/ -> Result detail
    """

    serializer_class = ApiCheckResultSerializer
    permission_classes = [IsProjectMember]
    filterset_fields = ['status', 'api_check', 'triggered_by']
    ordering_fields = ['created_at', 'latency_ms', 'status_code']
    ordering = ['-created_at']

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return ApiCheckResult.objects.none()
        return ApiCheckResult.objects.filter(
            api_check__project=project
        ).select_related('api_check', 'api_check__environment')