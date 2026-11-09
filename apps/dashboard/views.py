"""
API views for Dashboard.

Provides aggregated data for project overview, release detail, API health,
test intelligence, and issues views.
"""

import logging
from datetime import timedelta
from django.db.models import Count, Avg, Max, Min, Q, F, Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.dashboard.models import (
    DashboardView,
    WidgetConfig,
    UserDashboardPreference,
    DashboardSnapshot,
)
from apps.dashboard.serializers import (
    DashboardViewSerializer,
    DashboardViewCreateSerializer,
    WidgetConfigSerializer,
    WidgetConfigCreateSerializer,
    UserDashboardPreferenceSerializer,
    UserDashboardPreferenceUpdateSerializer,
    DashboardSnapshotSerializer,
    ProjectDashboardSummarySerializer,
    DashboardDataSerializer,
)
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

        # Check membership - handle both User (session) and Project (token auth)
        user = self.request.user
        if hasattr(user, 'is_superuser'):  # Django User (session auth)
            if not user.is_superuser:
                has_access = user.memberships.filter(
                    organisation=project.organisation,
                    is_active=True,
                    organisation__is_active=True,
                ).exists()
                if not has_access:
                    self.permission_denied(self.request, message='Not a member of this project\'s organisation')
        elif hasattr(user, 'is_authenticated') and user.is_authenticated:  # Project (token auth)
            # ProjectTokenAuthentication sets project.is_authenticated = True
            # The project itself is the authenticated entity
            if user.pk != project.pk:
                self.permission_denied(self.request, message='Token not valid for this project')
        else:
            self.permission_denied(self.request, message='Authentication required')

        return project


class DashboardDataViewSet(ProjectScopedViewSetMixin, viewsets.GenericViewSet):
    """
    Main dashboard data endpoints.

    Provides aggregated data for different dashboard views.
    """

    permission_classes = [IsProjectMember]

    def get_project(self):
        return super().get_project()

    @action(detail=False, methods=['get'])
    def overview(self, request, *args, **kwargs):
        """Get project overview dashboard data."""
        project = self.get_project()

        # Try to get cached snapshot
        context = {'project_id': str(project.id)}
        snapshot = DashboardSnapshot.get_valid_snapshot(project, 'project_overview', context)

        if snapshot:
            return Response({**snapshot.data, 'cached': True})

        # Generate fresh data
        data = self._generate_project_overview(project)

        # Cache for 5 minutes
        DashboardSnapshot.create_snapshot(project, 'project_overview', context, data, ttl_seconds=300)

        return Response({**data, 'cached': False})

    @action(detail=False, methods=['get'])
    def release_detail(self, request, *args, **kwargs):
        """Get release detail dashboard data."""
        project = self.get_project()
        release_id = request.query_params.get('release_id')

        if not release_id:
            return Response(
                {'error': {'code': 'validation_error', 'message': 'release_id is required'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try cache
        context = {'project_id': str(project.id), 'release_id': release_id}
        snapshot = DashboardSnapshot.get_valid_snapshot(project, 'release_detail', context)

        if snapshot:
            return Response({**snapshot.data, 'cached': True})

        data = self._generate_release_detail(project, release_id)
        DashboardSnapshot.create_snapshot(project, 'release_detail', context, data, ttl_seconds=300)

        return Response({**data, 'cached': False})

    @action(detail=False, methods=['get'])
    def api_health(self, request, *args, **kwargs):
        """Get API health dashboard data."""
        project = self.get_project()

        context = {'project_id': str(project.id)}
        snapshot = DashboardSnapshot.get_valid_snapshot(project, 'api_health', context)

        if snapshot:
            return Response({**snapshot.data, 'cached': True})

        data = self._generate_api_health(project)
        DashboardSnapshot.create_snapshot(project, 'api_health', context, data, ttl_seconds=300)

        return Response({**data, 'cached': False})

    @action(detail=False, methods=['get'])
    def test_intelligence(self, request, *args, **kwargs):
        """Get test intelligence dashboard data."""
        project = self.get_project()

        context = {'project_id': str(project.id)}
        snapshot = DashboardSnapshot.get_valid_snapshot(project, 'test_intelligence', context)

        if snapshot:
            return Response({**snapshot.data, 'cached': True})

        data = self._generate_test_intelligence(project)
        DashboardSnapshot.create_snapshot(project, 'test_intelligence', context, data, ttl_seconds=300)

        return Response({**data, 'cached': False})

    @action(detail=False, methods=['get'])
    def issues(self, request, *args, **kwargs):
        """Get issues dashboard data."""
        project = self.get_project()

        context = {'project_id': str(project.id)}
        snapshot = DashboardSnapshot.get_valid_snapshot(project, 'issues', context)

        if snapshot:
            return Response({**snapshot.data, 'cached': True})

        data = self._generate_issues_dashboard(project)
        DashboardSnapshot.create_snapshot(project, 'issues', context, data, ttl_seconds=300)

        return Response({**data, 'cached': False})

    @action(detail=False, methods=['get'])
    def summary(self, request, *args, **kwargs):
        """Get lightweight project summary for project list."""
        project = self.get_project()
        data = self._generate_project_summary(project)
        serializer = ProjectDashboardSummarySerializer(data)
        return Response(serializer.data)

    # ==================== Data Generation Methods ====================

    def _generate_project_overview(self, project):
        """Generate project overview data."""
        from apps.releases.models import Release, ReleaseAnalysis, TestRun
        from apps.issues.models import IssueGroup
        from apps.api_checks.models import ApiCheck, ApiCheckResult
        from django.db.models import Sum

        # Recent releases with prefetched test runs
        recent_releases = list(
            Release.objects.filter(project=project)
                     .select_related('environment')
                     .prefetch_related('test_runs')
                     .order_by('-deployed_at')[:10]
        )
        releases_data = []
        for r in recent_releases:
            analysis = getattr(r, 'analysis', None)
            completed_runs = [tr for tr in r.test_runs.all() if tr.status == 'completed']
            total_tests = sum(tr.total_tests for tr in completed_runs)
            failed_tests = sum(tr.failed_tests for tr in completed_runs)
            releases_data.append({
                'id': str(r.id),
                'version': r.version,
                'commit_short_sha': r.commit_short_sha,
                'branch': r.branch,
                'environment': r.environment.name,
                'environment_type': r.environment.type,
                'deployed_at': r.deployed_at,
                'status': analysis.status if analysis else 'pending',
                'total_tests': total_tests,
                'failed_tests': failed_tests,
            })

        # Key metrics
        total_releases = Release.objects.filter(project=project).count()
        recent_analyses = ReleaseAnalysis.objects.filter(release__project=project).order_by('-evaluated_at')[:20]
        green_count = sum(1 for a in recent_analyses if a.status == 'green')
        yellow_count = sum(1 for a in recent_analyses if a.status == 'yellow')
        red_count = sum(1 for a in recent_analyses if a.status == 'red')

        # Overall health
        if red_count > 0:
            health_status = 'red'
        elif yellow_count > 0:
            health_status = 'yellow'
        else:
            health_status = 'green'

        # Active issues
        active_issues = IssueGroup.objects.filter(
            project=project,
            status__in=['open', 'in_progress'],
        ).count()
        regressions = IssueGroup.objects.filter(
            project=project,
            is_regression=True,
            status__in=['open', 'in_progress'],
        ).count()

        # Failing API checks & API health summary
        failing_checks = ApiCheckResult.objects.filter(
            api_check__project=project,
            status__in=['failure', 'timeout', 'error'],
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).values('api_check').distinct().count()
        total_api_checks = ApiCheck.objects.filter(project=project, is_active=True).count()
        healthy_checks = max(0, total_api_checks - failing_checks)

        # Issues summary
        issues_open = IssueGroup.objects.filter(project=project, status='open').count()
        issues_in_progress = IssueGroup.objects.filter(project=project, status='in_progress').count()
        issues_resolved = IssueGroup.objects.filter(project=project, status='resolved').count()

        # Test trends (7d and 30d)
        now = timezone.now()
        runs_7d = list(TestRun.objects.filter(release__project=project, status='completed', created_at__gte=now - timedelta(days=7)))
        t7_total = sum(r.total_tests for r in runs_7d)
        t7_failed = sum(r.failed_tests for r in runs_7d)
        pass_rate_7d = round(((t7_total - t7_failed) / t7_total * 100.0), 1) if t7_total > 0 else 100.0

        runs_30d = list(TestRun.objects.filter(release__project=project, status='completed', created_at__gte=now - timedelta(days=30)))
        t30_total = sum(r.total_tests for r in runs_30d)
        t30_failed = sum(r.failed_tests for r in runs_30d)
        pass_rate_30d = round(((t30_total - t30_failed) / t30_total * 100.0), 1) if t30_total > 0 else 100.0

        flaky_tests = self._detect_flaky_tests(project, now - timedelta(days=30))
        flaky_count = len(flaky_tests)

        # Latest release
        latest_release = Release.objects.filter(project=project).order_by('-deployed_at').first()

        return {
            'project': {
                'id': str(project.id),
                'name': project.name,
                'slug': project.slug,
            },
            'health_status': health_status,
            'release_health': health_status.upper(),
            'total_releases': total_releases,
            'api_health_summary': {
                'healthy': healthy_checks,
                'unhealthy': failing_checks,
                'total': total_api_checks,
            },
            'issues_summary': {
                'open': issues_open,
                'in_progress': issues_in_progress,
                'resolved': issues_resolved,
            },
            'test_trends': {
                'pass_rate_7d': pass_rate_7d,
                'pass_rate_30d': pass_rate_30d,
                'flaky_count': flaky_count,
            },
            'recent_releases': releases_data,
            'key_metrics': {
                'total_releases': total_releases,
                'recent_green': green_count,
                'recent_yellow': yellow_count,
                'recent_red': red_count,
                'active_issues': active_issues,
                'regressions': regressions,
                'failing_api_checks': failing_checks,
            },
            'latest_release': {
                'id': str(latest_release.id),
                'version': latest_release.version,
                'status': getattr(latest_release, 'status', 'deployed'),
                'deployed_at': latest_release.deployed_at,
            } if latest_release else None,
            'widgets': self._get_default_overview_widgets(),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'project_id': str(project.id),
            },
        }

    def _generate_release_detail(self, project, release_id):
        """Generate release detail data."""
        from apps.releases.models import Release, ReleaseAnalysis, TestRun, TestCaseResult
        from apps.issues.models import ErrorEvent

        release = get_object_or_404(
            Release.objects.select_related('environment', 'analysis')
                     .prefetch_related(
                         'test_runs__test_cases',
                         'test_runs__environment',
                     ),
            id=release_id, project=project
        )

        # Release basic info
        release_data = {
            'id': str(release.id),
            'version': release.version,
            'commit_sha': release.commit_sha,
            'commit_short_sha': release.commit_short_sha,
            'branch': release.branch,
            'workflow_run_id': release.workflow_run_id,
            'workflow_run_url': release.workflow_run_url,
            'commit_message': release.commit_message,
            'commit_author': release.commit_author,
            'commit_timestamp': release.commit_timestamp,
            'deployed_at': release.deployed_at,
            'environment': {
                'id': str(release.environment.id),
                'name': release.environment.name,
                'type': release.environment.type,
            },
        }

        # Analysis
        analysis = getattr(release, 'analysis', None)
        analysis_data = None
        if analysis:
            analysis_data = {
                'status': analysis.status,
                'policy_version': analysis.policy_version,
                'rule_results': analysis.rule_results,
                'new_failures': analysis.new_failures,
                'persistent_failures': analysis.persistent_failures,
                'fixed_failures': analysis.fixed_failures,
                'flaky_tests': analysis.flaky_tests,
                'evaluated_at': analysis.evaluated_at,
            }

        # Test runs - use prefetched data to avoid N+1
        test_runs = list(release.test_runs.filter(status='completed').order_by('-created_at'))
        test_runs_data = []
        total_tests = 0
        total_failed = 0
        for tr in test_runs:
            tr_data = {
                'id': str(tr.id),
                'name': tr.name,
                'status': tr.status,
                'total_tests': tr.total_tests,
                'passed_tests': tr.passed_tests,
                'failed_tests': tr.failed_tests,
                'skipped_tests': tr.skipped_tests,
                'error_tests': tr.error_tests,
                'total_duration': tr.total_duration,
                'pass_rate': tr.pass_rate,
            }
            test_runs_data.append(tr_data)
            total_tests += tr.total_tests
            total_failed += tr.failed_tests

        # Failure breakdown - use prefetched test_cases
        failed_cases = []
        for tr in test_runs:
            for tc in tr.test_cases.filter(status__in=['failed', 'error']):
                failed_cases.append(tc)

        new_failures = []
        persistent_failures = []
        fixed_failures = []

        if hasattr(release, 'analysis') and release.analysis:
            # Get comparison data
            comparison = release.analysis.get_failed_rules()  # This is rules, not test cases
            # We'd need to access comparison service for detailed breakdown
            pass

        # Error events for this release
        error_events = ErrorEvent.objects.filter(
            release=release
        ).select_related('issue_group').order_by('-occurred_at')[:20]

        error_events_data = []
        for ee in error_events:
            error_events_data.append({
                'id': str(ee.id),
                'fingerprint': ee.fingerprint,
                'exception_class': ee.exception_class,
                'message': ee.message[:200] if ee.message else '',
                'source': ee.source,
                'occurred_at': ee.occurred_at,
                'issue_group': {
                    'id': str(ee.issue_group.id),
                    'title': ee.issue_group.title,
                    'status': ee.issue_group.status,
                } if ee.issue_group else None,
            })

        # Comparison with previous release
        comparison_data = None
        prev_release = release.previous_release
        if prev_release:
            comparison_data = {
                'previous_release': {
                    'id': str(prev_release.id),
                    'version': prev_release.version,
                    'deployed_at': prev_release.deployed_at,
                },
                # Add comparison metrics here
            }

        return {
            'release': release_data,
            'analysis': analysis_data,
            'test_runs': test_runs_data,
            'summary': {
                'total_tests': total_tests,
                'total_failed': total_failed,
                'pass_rate': ((total_tests - total_failed) / total_tests * 100) if total_tests > 0 else 0,
            },
            'error_events': error_events_data,
            'comparison': comparison_data,
            'widgets': self._get_default_release_detail_widgets(),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'release_id': release_id,
            },
        }

    def _generate_api_health(self, project):
        """Generate API health dashboard data."""
        from apps.api_checks.models import ApiCheck, ApiCheckResult

        # All checks for project
        checks = ApiCheck.objects.filter(project=project, is_active=True).select_related('environment')
        checks_data = []

        for check in checks:
            # Recent results (last 24 hours)
            recent_results = ApiCheckResult.objects.filter(
                api_check=check,
                created_at__gte=timezone.now() - timedelta(hours=24),
            ).order_by('-created_at')

            total_24h = recent_results.count()
            success_24h = recent_results.filter(status='success').count()
            success_rate = (success_24h / total_24h * 100) if total_24h > 0 else 0

            # Average latency
            avg_latency = recent_results.filter(
                status='success',
                latency_ms__isnull=False,
            ).aggregate(avg=Avg('latency_ms'))['avg']

            # Last result
            last_result = recent_results.first()
            last_status = last_result.status if last_result else 'unknown'

            checks_data.append({
                'id': str(check.id),
                'name': check.name,
                'url': check.url,
                'method': check.method,
                'environment': check.environment.name if check.environment else None,
                'expected_status': check.expected_status,
                'interval_seconds': check.interval_seconds,
                'is_critical': check.is_critical,
                'last_status': last_status,
                'last_check_at': last_result.created_at if last_result else None,
                'success_rate_24h': round(success_rate, 1),
                'avg_latency_ms': round(avg_latency) if avg_latency else None,
                'total_checks_24h': total_24h,
            })

        # Overall stats
        total_checks = len(checks_data)
        healthy_checks = sum(1 for c in checks_data if c['last_status'] == 'success')
        critical_failing = sum(1 for c in checks_data if c['is_critical'] and c['last_status'] != 'success')

        # Latency trend (last 7 days)
        latency_trend = self._get_latency_trend(project)

        return {
            'project': {'id': str(project.id), 'name': project.name},
            'checks': checks_data,
            'summary': {
                'total_checks': total_checks,
                'healthy_checks': healthy_checks,
                'critical_failing': critical_failing,
                'overall_health': 'healthy' if critical_failing == 0 else 'degraded',
            },
            'latency_trend': latency_trend,
            'widgets': self._get_default_api_health_widgets(),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'project_id': str(project.id),
            },
        }

    def _generate_test_intelligence(self, project):
        """Generate test intelligence dashboard data."""
        from apps.releases.models import Release, TestRun, TestCaseResult

        # Get recent test runs (last 30 days)
        since = timezone.now() - timedelta(days=30)
        test_runs = TestRun.objects.filter(
            release__project=project,
            status='completed',
            created_at__gte=since,
        ).select_related('release', 'release__environment')

        # Overall trends
        daily_stats = test_runs.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            total=Sum('total_tests'),
            passed=Sum('passed_tests'),
            failed=Sum('failed_tests'),
            duration=Avg('total_duration'),
        ).order_by('day')

        # Flaky tests detection
        flaky_tests = self._detect_flaky_tests(project, since)

        # Top failing tests
        top_failures = TestCaseResult.objects.filter(
            test_run__release__project=project,
            test_run__created_at__gte=since,
            status__in=['failed', 'error'],
        ).values('classname', 'name').annotate(
            failure_count=Count('id')
        ).order_by('-failure_count')[:20]

        # Duration trends
        duration_trends = test_runs.values('release__version').annotate(
            avg_duration=Avg('total_duration'),
            total_tests=Sum('total_tests'),
        ).order_by('-release__deployed_at')[:20]

        # New failures (tests that passed before but fail now)
        new_failures = self._get_new_failures(project, since)

        return {
            'project': {'id': str(project.id), 'name': project.name},
            'daily_stats': list(daily_stats),
            'flaky_tests': flaky_tests,
            'top_failures': list(top_failures),
            'duration_trends': list(duration_trends),
            'new_failures': new_failures,
            'widgets': self._get_default_test_intelligence_widgets(),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'project_id': str(project.id),
                'period_days': 30,
            },
        }

    def _generate_issues_dashboard(self, project):
        """Generate issues dashboard data."""
        from apps.issues.models import IssueGroup, ErrorEvent

        # Issue groups by status
        status_counts = IssueGroup.objects.filter(project=project).values('status').annotate(
            count=Count('id')
        )

        # Recent issues
        recent_issues = IssueGroup.objects.filter(
            project=project
        ).order_by('-last_seen_at')[:20]

        issues_data = []
        for issue in recent_issues:
            issues_data.append({
                'id': str(issue.id),
                'title': issue.title,
                'fingerprint': issue.fingerprint[:8],
                'status': issue.status,
                'is_regression': issue.is_regression,
                'occurrence_count': issue.occurrence_count,
                'first_seen_at': issue.first_seen_at,
                'last_seen_at': issue.last_seen_at,
                'assigned_to': issue.assigned_to.email if issue.assigned_to else None,
            })

        # Top errors by occurrence
        top_errors = IssueGroup.objects.filter(
            project=project,
            status__in=['open', 'in_progress'],
        ).order_by('-occurrence_count')[:10]

        # Regressions
        regressions = IssueGroup.objects.filter(
            project=project,
            is_regression=True,
            status__in=['open', 'in_progress'],
        ).order_by('-last_seen_at')[:10]

        # Error trend (last 30 days)
        since = timezone.now() - timedelta(days=30)
        error_trend = ErrorEvent.objects.filter(
            project=project,
            occurred_at__gte=since,
        ).extra(select={'day': 'date(occurred_at)'}).values('day').annotate(
            count=Count('id')
        ).order_by('day')

        return {
            'project': {'id': str(project.id), 'name': project.name},
            'status_counts': {item['status']: item['count'] for item in status_counts},
            'recent_issues': issues_data,
            'top_errors': [
                {
                    'id': str(e.id),
                    'title': e.title,
                    'occurrence_count': e.occurrence_count,
                    'status': e.status,
                } for e in top_errors
            ],
            'regressions': [
                {
                    'id': str(e.id),
                    'title': e.title,
                    'last_seen_at': e.last_seen_at,
                    'occurrence_count': e.occurrence_count,
                } for e in regressions
            ],
            'error_trend': list(error_trend),
            'widgets': self._get_default_issues_widgets(),
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'project_id': str(project.id),
            },
        }

    def _generate_project_summary(self, project):
        """Generate lightweight project summary."""
        from apps.releases.models import Release, ReleaseAnalysis
        from apps.issues.models import IssueGroup
        from apps.api_checks.models import ApiCheckResult

        latest_release = Release.objects.filter(project=project).order_by('-deployed_at').first()
        recent_analysis = ReleaseAnalysis.objects.filter(release__project=project).order_by('-evaluated_at').first()

        if recent_analysis:
            health_status = recent_analysis.status
        else:
            health_status = 'unknown'

        active_issues = IssueGroup.objects.filter(
            project=project,
            status__in=['open', 'in_progress'],
        ).count()

        failing_checks = ApiCheckResult.objects.filter(
            api_check__project=project,
            status__in=['failure', 'timeout', 'error'],
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).values('api_check').distinct().count()

        return {
            'project_id': str(project.id),
            'project_name': project.name,
            'project_slug': project.slug,
            'health_status': health_status,
            'recent_release': {
                'id': str(latest_release.id),
                'version': latest_release.version,
                'deployed_at': latest_release.deployed_at,
            } if latest_release else None,
            'key_metrics': {
                'active_issues': active_issues,
                'failing_api_checks': failing_checks,
            },
            'failing_api_checks': failing_checks,
            'last_updated': timezone.now(),
        }

    # ==================== Helper Methods ====================

    def _get_latency_trend(self, project):
        """Get latency trend for last 7 days."""
        from apps.api_checks.models import ApiCheckResult

        since = timezone.now() - timedelta(days=7)
        daily_latency = ApiCheckResult.objects.filter(
            api_check__project=project,
            status='success',
            latency_ms__isnull=False,
            created_at__gte=since,
        ).extra(select={'day': 'date(created_at)'}).values('day').annotate(
            avg_latency=Avg('latency_ms'),
            count=Count('id'),
        ).order_by('day')

        return list(daily_latency)

    def _detect_flaky_tests(self, project, since):
        """Detect flaky tests in given period."""
        from apps.releases.models import TestRun, TestCaseResult

        # Tests that have both passed and failed
        test_statuses = TestCaseResult.objects.filter(
            test_run__release__project=project,
            test_run__created_at__gte=since,
            test_run__status='completed',
        ).values('classname', 'name', 'status').distinct()

        # Group by test identifier
        from collections import defaultdict
        test_status_map = defaultdict(set)
        for ts in test_statuses:
            key = f"{ts['classname']}.{ts['name']}"
            test_status_map[key].add(ts['status'])

        flaky = []
        for test_id, statuses in test_status_map.items():
            if 'passed' in statuses and ('failed' in statuses or 'error' in statuses):
                flaky.append({
                    'test_identifier': test_id,
                    'statuses': list(statuses),
                })

        return flaky[:50]

    def _get_new_failures(self, project, since):
        """Get tests that started failing in the period."""
        from apps.releases.models import TestRun, TestCaseResult

        # Tests that failed in period but passed before
        current_failures = TestCaseResult.objects.filter(
            test_run__release__project=project,
            test_run__created_at__gte=since,
            test_run__status='completed',
            status__in=['failed', 'error'],
        ).values('classname', 'name')

        # This is simplified - full implementation would compare with previous period
        return list(current_failures[:20])

    # ==================== Default Widget Configurations ====================

# ==================== Default Widget Configurations ====================

    WIDGET_CONFIGS = {
        'overview': [
            {'widget_type': 'health_summary', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'recent_releases', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 10}},
            {'widget_type': 'key_metrics', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'trend_chart', 'size': {'w': 6, 'h': 4}, 'config': {'metric': 'pass_rate', 'days': 30}},
        ],
        'release_detail': [
            {'widget_type': 'release_header', 'size': {'w': 12, 'h': 3}, 'config': {}},
            {'widget_type': 'test_summary', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'comparison_chart', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'policy_explanation', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'failure_breakdown', 'size': {'w': 12, 'h': 6}, 'config': {}},
        ],
        'api_health': [
            {'widget_type': 'api_check_list', 'size': {'w': 12, 'h': 6}, 'config': {}},
            {'widget_type': 'latency_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 7}},
            {'widget_type': 'uptime_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'status_timeline', 'size': {'w': 12, 'h': 4}, 'config': {'hours': 24}},
        ],
        'test_intelligence': [
            {'widget_type': 'test_trends', 'size': {'w': 12, 'h': 5}, 'config': {'days': 30}},
            {'widget_type': 'flaky_tests', 'size': {'w': 6, 'h': 5}, 'config': {'limit': 20}},
            {'widget_type': 'duration_trends', 'size': {'w': 6, 'h': 5}, 'config': {}},
            {'widget_type': 'new_failures', 'size': {'w': 12, 'h': 4}, 'config': {'limit': 10}},
        ],
        'issues': [
            {'widget_type': 'issue_list', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 20}},
            {'widget_type': 'issue_trend', 'size': {'w': 12, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'top_errors', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
            {'widget_type': 'regression_alerts', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
        ],
    }

    def _get_widgets(self, view_type):
        """Get default widget configuration for a dashboard view type."""
        return self.WIDGET_CONFIGS.get(view_type, [])

    def _get_default_overview_widgets(self):
        return self._get_widgets('overview')

    def _get_default_release_detail_widgets(self):
        return self._get_widgets('release_detail')

    def _get_default_api_health_widgets(self):
        return self._get_widgets('api_health')

    def _get_default_test_intelligence_widgets(self):
        return self._get_widgets('test_intelligence')

    def _get_default_issues_widgets(self):
        return self._get_widgets('issues')


class DashboardViewViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for DashboardView management."""

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return DashboardView.objects.none()
        return DashboardView.objects.filter(project=project).select_related('user')

    def get_serializer_class(self):
        if self.action == 'create':
            return DashboardViewCreateSerializer
        return DashboardViewSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project, user=self.request.user)


class WidgetConfigViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for WidgetConfig management."""

    permission_classes = [IsProjectAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return WidgetConfig.objects.none()
        return WidgetConfig.objects.filter(project=project)

    def get_serializer_class(self):
        if self.action == 'create':
            return WidgetConfigCreateSerializer
        return WidgetConfigSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project)


class UserDashboardPreferenceViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for UserDashboardPreference management."""

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return UserDashboardPreference.objects.none()
        return UserDashboardPreference.objects.filter(project=project).select_related('user', 'default_view')

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserDashboardPreferenceUpdateSerializer
        return UserDashboardPreferenceSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def get_object(self):
        """Get or create preference for current user."""
        project = self.get_project()
        preference, created = UserDashboardPreference.objects.get_or_create(
            user=self.request.user,
            project=project,
        )
        return preference

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request, *args, **kwargs):
        """Get or update current user's preferences."""
        return self.retrieve(request, *args, **kwargs) if request.method == 'GET' else self.update(request, *args, **kwargs)


# Import timezone
from django.utils import timezone