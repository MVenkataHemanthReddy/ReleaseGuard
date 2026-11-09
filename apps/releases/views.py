"""
API views for ReleaseGuard releases.

Handles release registration, JUnit XML ingestion, and dashboard queries.
"""

import logging
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.releases.serializers import (
    ReleaseSerializer,
    ReleaseCreateSerializer,
    TestRunSerializer,
    TestRunUploadSerializer,
    TestCaseResultSerializer,
    ReleaseAnalysisSerializer,
    ReleaseCompareSerializer,
    ReleaseDashboardSerializer,
)
from apps.releases.services import (
    TestRunProcessingService,
    ReleaseAnalysisService,
    ReleaseComparisonService,
)
from apps.projects.models import Project
from apps.core.permissions import IsProjectMember, CanManageReleases
from apps.core.exceptions import custom_exception_handler

logger = logging.getLogger(__name__)


class ProjectScopedViewSetMixin:
    """
    Mixin to scope all queries to user's projects via organisation membership.
    """

    def get_project(self):
        """Get project from URL kwargs, with permission check."""
        project_id = self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        if not project_id:
            return None

        project = get_object_or_404(Project, pk=project_id)

        # Check membership based on auth type
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
        elif hasattr(user, 'is_authenticated') and hasattr(user, '_project_token'):  # ProjectToken auth - Project object
            # The project itself is the authenticated "user"
            if user.pk != project.pk:
                self.permission_denied(self.request, message='Token not valid for this project')
        else:
            self.permission_denied(self.request, message='Authentication required')

        return project


class ReleaseViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Release management.

    Endpoints:
    - POST   /api/v1/projects/{project_pk}/releases/     -> Create/register release
    - GET    /api/v1/projects/{project_pk}/releases/     -> List releases
    - GET    /api/v1/projects/{project_pk}/releases/{pk}/ -> Release detail
    - GET    /api/v1/projects/{project_pk}/releases/{pk}/compare/ -> Compare with previous
    - GET    /api/v1/projects/{project_pk}/releases/dashboard/ -> Dashboard summary
    """

    serializer_class = ReleaseSerializer
    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return Release.objects.none()
        return Release.objects.filter(project=project).select_related(
            'environment', 'analysis'
        ).prefetch_related('test_runs')

    def get_serializer_class(self):
        if self.action == 'create':
            return ReleaseCreateSerializer
        if self.action == 'dashboard':
            return ReleaseDashboardSerializer
        return ReleaseSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def create(self, request, *args, **kwargs):
        """Register a new release (idempotent by workflow_run_id)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        release = serializer.save()
        return Response(
            ReleaseSerializer(release, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def compare(self, request, *args, **kwargs):
        """Compare this release with the previous release in same project+environment."""
        release = self.get_object()

        # Get comparison
        comparison_service = ReleaseComparisonService(release)
        comparison = comparison_service.compare()

        # Serialize current and previous releases
        current_serializer = ReleaseSerializer(release, context=self.get_serializer_context())
        previous_serializer = None
        if comparison_service.previous_release:
            previous_serializer = ReleaseSerializer(
                comparison_service.previous_release,
                context=self.get_serializer_context(),
            )

        # Serialize test case categories
        new_failures_serializer = TestCaseResultSerializer(comparison.new_failures, many=True, context=self.get_serializer_context())
        persistent_failures_serializer = TestCaseResultSerializer(comparison.persistent_failures, many=True, context=self.get_serializer_context())
        fixed_failures_serializer = TestCaseResultSerializer(comparison.fixed_failures, many=True, context=self.get_serializer_context())
        unchanged_passing_serializer = TestCaseResultSerializer(comparison.unchanged_passing, many=True, context=self.get_serializer_context())

        # Summary
        summary = {
            'total_new_failures': len(comparison.new_failures),
            'total_persistent_failures': len(comparison.persistent_failures),
            'total_fixed_failures': len(comparison.fixed_failures),
            'total_unchanged_passing': len(comparison.unchanged_passing),
        }

        return Response({
            'current_release': current_serializer.data,
            'previous_release': previous_serializer.data if previous_serializer else None,
            'new_failures': new_failures_serializer.data,
            'persistent_failures': persistent_failures_serializer.data,
            'fixed_failures': fixed_failures_serializer.data,
            'unchanged_passing': unchanged_passing_serializer.data,
            'summary': summary,
        })

    @action(detail=False, methods=['get'])
    def dashboard(self, request, *args, **kwargs):
        """Lightweight release list for project dashboard."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TestRunUploadView(ProjectScopedViewSetMixin, viewsets.GenericViewSet):
    """
    View for uploading JUnit XML test results.

    Endpoint:
    - POST /api/v1/releases/{release_pk}/test-runs/ -> Upload test results
    """

    permission_classes = [CanManageReleases]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = TestRunUploadSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsProjectMember()]
        return [CanManageReleases()]

    def list(self, request, *args, **kwargs):
        release = self.get_release()
        test_runs = TestRun.objects.filter(release=release).order_by('-created_at')
        serializer = TestRunSerializer(test_runs, many=True, context=self.get_serializer_context())
        return Response({'results': serializer.data, 'count': len(serializer.data)})

    def get_release(self):
        """Get release from URL, with permission check."""
        release_id = self.kwargs.get('release_pk')
        release = get_object_or_404(Release, pk=release_id)

        # Check project membership
        user = self.request.user
        if not user.is_superuser:
            has_access = user.memberships.filter(
                organisation=release.project.organisation,
                is_active=True,
                organisation__is_active=True,
            ).exists()
            if not has_access:
                self.permission_denied(self.request, message='Not a member of this project\'s organisation')

        return release

    def create(self, request, *args, **kwargs):
        """
        Upload JUnit XML for a release.

        Accepts:
        - multipart/form-data with 'junit_xml' file field
        - application/json with 'junit_xml' string field
        """
        release = self.get_release()

        # Handle both file upload and JSON
        if 'junit_xml' in request.FILES:
            xml_content = request.FILES['junit_xml'].read().decode('utf-8')
        else:
            xml_content = request.data.get('junit_xml', '')

        # Validate with serializer
        serializer = self.get_serializer(data={
            'test_run_name': request.data.get('test_run_name', 'default'),
            'junit_xml': xml_content,
            'idempotency_key': request.data.get('idempotency_key', ''),
        })
        serializer.is_valid(raise_exception=True)

        test_run_name = serializer.validated_data['test_run_name']
        idempotency_key = serializer.validated_data.get('idempotency_key') or f'{release.workflow_run_id}:{test_run_name}'

        # Process upload (parsing + storage)
        processing_service = TestRunProcessingService(release)
        test_run = processing_service.process_upload(
            xml_content=xml_content,
            test_run_name=test_run_name,
            idempotency_key=idempotency_key,
        )

        # Trigger analysis asynchronously (background job)
        self._queue_analysis_job(release)

        return Response(
            TestRunSerializer(test_run, context=self.get_serializer_context()).data,
            status=status.HTTP_202_ACCEPTED,
        )

    def _queue_analysis_job(self, release: Release):
        """Queue a background job to generate release analysis."""
        from apps.core.models import BackgroundJob
        import uuid

        worker_id = f'web-{uuid.uuid4().hex[:8]}'

        job = BackgroundJob.objects.create(
            name='generate_release_analysis',
            payload={
                'release_id': str(release.id),
                'policy_version': '1.0',
            },
            priority=BackgroundJob.Priority.HIGH,
            idempotency_key=f'analysis:{release.id}',
            worker_id=worker_id,
        )
        logger.info('Queued analysis job %s for release %s', job.id, release)


class TestRunViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for TestRun queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/test-runs/ -> List test runs
    - GET /api/v1/projects/{project_pk}/test-runs/{pk}/ -> Test run detail
    """

    serializer_class = TestRunSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return TestRun.objects.none()
        return TestRun.objects.filter(
            release__project=project
        ).select_related('release', 'release__environment')


class TestCaseResultViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for TestCaseResult queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/test-cases/ -> List test cases (with filters)
    """

    serializer_class = TestCaseResultSerializer
    permission_classes = [IsProjectMember]
    filterset_fields = ['status', 'test_run', 'test_run__release']
    search_fields = ['classname', 'name', 'message']
    ordering_fields = ['duration', 'created_at', 'classname', 'name']
    ordering = ['classname', 'name']

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return TestCaseResult.objects.none()
        return TestCaseResult.objects.filter(
            test_run__release__project=project
        ).select_related('test_run', 'test_run__release')


class ReleaseAnalysisViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for ReleaseAnalysis queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/analyses/ -> List analyses
    - GET /api/v1/projects/{project_pk}/analyses/{pk}/ -> Analysis detail
    """

    serializer_class = ReleaseAnalysisSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return ReleaseAnalysis.objects.none()
        return ReleaseAnalysis.objects.filter(
            release__project=project
        ).select_related('release', 'release__environment', 'compared_to_release')