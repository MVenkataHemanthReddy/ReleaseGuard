"""
API views for Issues.
"""

import logging
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.issues.models import IssueGroup, ErrorEvent
from apps.issues.serializers import (
    IssueGroupSerializer,
    IssueGroupDetailSerializer,
    IssueGroupUpdateSerializer,
    ErrorEventSerializer,
    ErrorEventCreateSerializer,
)
from apps.issues.services import IssueGroupService, ErrorEventIngestionService
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


class IssueGroupViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Issue Group management.

    Endpoints:
    - GET    /api/v1/projects/{project_pk}/issues/              -> List issue groups
    - POST   /api/v1/projects/{project_pk}/issues/              -> Create issue group (manual)
    - GET    /api/v1/projects/{project_pk}/issues/{pk}/         -> Issue group detail
    - PATCH  /api/v1/projects/{project_pk}/issues/{pk}/         -> Update issue group (status, assignment)
    - DELETE /api/v1/projects/{project_pk}/issues/{pk}/         -> Soft delete issue group
    - POST   /api/v1/projects/{project_pk}/issues/{pk}/resolve/ -> Mark as resolved
    - POST   /api/v1/projects/{project_pk}/issues/{pk}/reopen/  -> Reopen issue
    """

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return IssueGroup.objects.none()
        return IssueGroup.objects.filter(project=project).select_related(
            'first_seen_release', 'last_seen_release', 'assigned_to'
        ).prefetch_related('error_events')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IssueGroupDetailSerializer
        if self.action in ['partial_update', 'update']:
            return IssueGroupUpdateSerializer
        return IssueGroupSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def create(self, request, *args, **kwargs):
        """Create issue group manually (for manual error reporting)."""
        serializer = ErrorEventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = self.get_project()
        validated = serializer.validated_data

        # Get optional release and environment
        release = None
        if validated.get('release_id'):
            from apps.releases.models import Release
            release = Release.objects.filter(project=project, id=validated['release_id']).first()

        environment = None
        if validated.get('environment_id'):
            from apps.projects.models import Environment
            environment = Environment.objects.filter(project=project, id=validated['environment_id']).first()

        # Ingest error event
        ingestion_service = ErrorEventIngestionService()
        error_event = ingestion_service.ingest_manual_error(
            project=project,
            fingerprint=validated['fingerprint'],
            exception_class=validated['exception_class'],
            message=validated.get('message', ''),
            traceback=validated.get('traceback', ''),
            context=validated.get('context', {}),
            release=release,
            environment=environment,
        )

        # Return the issue group
        issue_group = error_event.issue_group
        response_serializer = IssueGroupDetailSerializer(issue_group, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def resolve(self, request, *args, **kwargs):
        """Mark issue group as resolved."""
        issue_group = self.get_object()
        service = IssueGroupService()
        service.update_status(issue_group, IssueGroup.Status.RESOLVED, user=request.user)
        serializer = self.get_serializer(issue_group)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def reopen(self, request, *args, **kwargs):
        """Reopen a resolved/ignored issue group."""
        issue_group = self.get_object()
        service = IssueGroupService()
        service.update_status(issue_group, IssueGroup.Status.OPEN, user=request.user)
        serializer = self.get_serializer(issue_group)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def mark_regression(self, request, *args, **kwargs):
        """Mark issue group as a regression."""
        issue_group = self.get_object()
        service = IssueGroupService()
        service.mark_regression(issue_group)
        serializer = self.get_serializer(issue_group)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def assign(self, request, *args, **kwargs):
        """Assign issue group to user."""
        issue_group = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': {'code': 'validation_error', 'message': 'user_id is required'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.accounts.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': {'code': 'not_found', 'message': 'User not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = IssueGroupService()
        service.assign(issue_group, user)
        serializer = self.get_serializer(issue_group)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None, **kwargs):
        """List error events for an issue group."""
        issue_group = self.get_object()
        events = ErrorEvent.objects.filter(issue_group=issue_group).order_by('-occurred_at')
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = ErrorEventSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ErrorEventSerializer(events, many=True)
        return Response({'results': serializer.data, 'count': len(serializer.data)})


class ErrorEventViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for ErrorEvent queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/error-events/ -> List error events
    - GET /api/v1/projects/{project_pk}/error-events/{pk}/ -> Error event detail
    """

    serializer_class = ErrorEventSerializer
    permission_classes = [IsProjectMember]
    filterset_fields = ['source', 'issue_group', 'release', 'environment']
    ordering_fields = ['occurred_at', 'created_at']
    ordering = ['-occurred_at']

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return ErrorEvent.objects.none()
        return ErrorEvent.objects.filter(project=project).select_related(
            'issue_group', 'release', 'environment'
        )