"""
Services for Issue Grouping in ReleaseGuard.

Handles error event ingestion, fingerprint-based grouping, and issue group lifecycle.
"""

import logging
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.issues.models import IssueGroup, ErrorEvent
from apps.releases.models import Release, TestCaseResult
from apps.api_checks.models import ApiCheckResult
from apps.releases.parsers import generate_test_fingerprint

logger = logging.getLogger(__name__)


class IssueGroupingService:
    """
    Service for grouping error events into issue groups by fingerprint.

    Deterministic grouping: same fingerprint -> same issue group.
    """

    @transaction.atomic
    def process_test_failure(
        self,
        test_case: TestCaseResult,
        release: Release,
    ) -> ErrorEvent:
        """
        Process a failed test case and create/link error event.

        Args:
            test_case: Failed TestCaseResult
            release: Parent Release

        Returns:
            Created ErrorEvent
        """
        # Generate fingerprint (already on test_case, but regenerate for consistency)
        fingerprint = test_case.fingerprint or generate_test_fingerprint(
            test_case.classname,
            test_case.name,
            test_case.traceback,
        )

        return self._create_error_event(
            project=release.project,
            release=release,
            environment=release.environment,
            fingerprint=fingerprint,
            exception_class=test_case.properties.get('exception_class', ''),
            message=test_case.message,
            traceback=test_case.traceback,
            source=ErrorEvent.Source.TEST_FAILURE,
            source_id=str(test_case.id),
            context={
                'test_classname': test_case.classname,
                'test_name': test_case.name,
                'test_status': test_case.status,
                'test_duration': test_case.duration,
                'test_run_id': str(test_case.test_run_id),
                'test_run_name': test_case.test_run.name,
            },
        )

    @transaction.atomic
    def process_api_check_failure(
        self,
        api_check_result: ApiCheckResult,
        release: Optional[Release] = None,
    ) -> ErrorEvent:
        """
        Process a failed API check result and create/link error event.

        Args:
            api_check_result: Failed ApiCheckResult
            release: Optional Release (if triggered by release deployment)

        Returns:
            Created ErrorEvent
        """
        # Generate fingerprint from error details
        fingerprint = generate_test_fingerprint(
            f'ApiCheck:{api_check_result.api_check.name}',
            api_check_result.error_type or 'UnknownError',
            api_check_result.error_message,
        )

        return self._create_error_event(
            project=api_check_result.api_check.project,
            release=release,
            environment=api_check_result.api_check.environment,
            fingerprint=fingerprint,
            exception_class=api_check_result.error_type or 'ApiCheckError',
            message=api_check_result.error_message,
            traceback='',  # API checks typically don't have tracebacks
            source=ErrorEvent.Source.API_CHECK,
            source_id=str(api_check_result.id),
            context={
                'api_check_name': api_check_result.api_check.name,
                'api_check_url': api_check_result.api_check.url,
                'status_code': api_check_result.status_code,
                'latency_ms': api_check_result.latency_ms,
                'ssl_valid': api_check_result.ssl_valid,
            },
        )

    def _create_error_event(
        self,
        project,
        fingerprint: str,
        exception_class: str,
        message: str,
        traceback: str,
        source: str,
        source_id: str,
        context: dict,
        release: Optional[Release] = None,
        environment=None,
    ) -> ErrorEvent:
        """
        Create error event and link to issue group.

        Uses fingerprint to find or create IssueGroup.
        """
        # Find or create issue group
        issue_group, created = IssueGroup.objects.get_or_create(
            project=project,
            fingerprint=fingerprint,
            defaults={
                'title': self._generate_title(exception_class, message, source),
                'description': self._generate_description(message, traceback, source),
                'error_type': source,
                'exception_class': exception_class,
                'first_seen_release': release,
                'last_seen_release': release,
                'tags': self._generate_tags(source, context),
            }
        )

        if not created:
            # Update existing group
            issue_group.increment_occurrence(release)

        # Create error event
        error_event = ErrorEvent.objects.create(
            issue_group=issue_group,
            project=project,
            release=release,
            environment=environment,
            fingerprint=fingerprint,
            exception_class=exception_class,
            message=message[:1000] if message else '',
            traceback=traceback[:5000] if traceback else '',
            source=source,
            source_id=source_id,
            context=context,
            occurred_at=timezone.now(),
        )

        logger.info(
            'Error event %s created for issue group %s (%s)',
            error_event.id,
            issue_group.id,
            'new' if created else 'existing',
        )

        return error_event

    def _generate_title(self, exception_class: str, message: str, source: str) -> str:
        """Generate human-readable title for issue group."""
        if exception_class:
            base = exception_class
        elif message:
            # Truncate message
            base = message[:100]
        else:
            base = 'Unknown Error'

        source_label = {
            ErrorEvent.Source.TEST_FAILURE: 'Test',
            ErrorEvent.Source.API_CHECK: 'API Check',
            ErrorEvent.Source.MANUAL: 'Manual',
        }.get(source, 'Error')

        return f'{source_label}: {base}'

    def _generate_description(self, message: str, traceback: str, source: str) -> str:
        """Generate description for issue group."""
        parts = []
        if message:
            parts.append(f'Message: {message[:500]}')
        if traceback:
            parts.append(f'Traceback:\n{traceback[:2000]}')
        parts.append(f'Source: {source}')
        return '\n\n'.join(parts)

    def _generate_tags(self, source: str, context: dict) -> dict:
        """Generate tags from context."""
        tags = {'source': source}
        if context.get('test_classname'):
            tags['test_class'] = context['test_classname']
        if context.get('api_check_name'):
            tags['api_check'] = context['api_check_name']
        return tags


class IssueGroupService:
    """
    Service for managing issue group lifecycle.

    Handles status transitions, assignment, regression detection.
    """

    def update_status(
        self,
        issue_group: IssueGroup,
        new_status: str,
        user=None,
    ) -> IssueGroup:
        """Update issue group status with transition validation."""
        valid_statuses = [c.value for c in IssueGroup.Status]
        if new_status not in valid_statuses:
            raise ValueError(f'Invalid status: {new_status}')

        # Validate status transitions
        valid_transitions = {
            IssueGroup.Status.OPEN: [IssueGroup.Status.IN_PROGRESS, IssueGroup.Status.RESOLVED, IssueGroup.Status.IGNORED],
            IssueGroup.Status.IN_PROGRESS: [IssueGroup.Status.RESOLVED, IssueGroup.Status.OPEN, IssueGroup.Status.IGNORED],
            IssueGroup.Status.RESOLVED: [IssueGroup.Status.OPEN],  # Reopen
            IssueGroup.Status.IGNORED: [IssueGroup.Status.OPEN],
        }

        old_status = issue_group.status
        if old_status in valid_transitions:
            if new_status not in valid_transitions[old_status]:
                raise ValueError(f'Cannot transition from {old_status} to {new_status}')

        issue_group.status = new_status

        if new_status == IssueGroup.Status.IN_PROGRESS and old_status == IssueGroup.Status.OPEN:
            issue_group.assigned_to = user

        if new_status == IssueGroup.Status.RESOLVED:
            issue_group.assigned_to = user

        issue_group.save(update_fields=['status', 'assigned_to', 'updated_at'])
        logger.info('Issue group %s status changed: %s -> %s', issue_group.id, old_status, new_status)
        return issue_group

    def mark_regression(self, issue_group: IssueGroup) -> IssueGroup:
        """Mark issue group as a regression."""
        if not issue_group.is_regression:
            issue_group.is_regression = True
            issue_group.save(update_fields=['is_regression', 'updated_at'])
            logger.warning('Issue group %s marked as regression', issue_group.id)
        return issue_group

    def assign(self, issue_group: IssueGroup, user) -> IssueGroup:
        """Assign issue group to user."""
        issue_group.assigned_to = user
        if issue_group.status == IssueGroup.Status.OPEN:
            issue_group.status = IssueGroup.Status.IN_PROGRESS
        issue_group.save(update_fields=['assigned_to', 'status', 'updated_at'])
        return issue_group

    def add_tags(self, issue_group: IssueGroup, tags: dict) -> IssueGroup:
        """Add tags to issue group."""
        issue_group.tags.update(tags)
        issue_group.save(update_fields=['tags', 'updated_at'])
        return issue_group


class ErrorEventIngestionService:
    """
    High-level service for ingesting error events from various sources.

    Entry point for background jobs and API endpoints.
    """

    def __init__(self):
        self.grouping_service = IssueGroupingService()

    def ingest_test_failure(self, test_case_id: str) -> ErrorEvent:
        """Ingest error from failed test case."""
        test_case = TestCaseResult.objects.select_related('test_run', 'test_run__release').get(id=test_case_id)
        if not test_case.is_failure:
            raise ValueError('Test case is not a failure')
        return self.grouping_service.process_test_failure(test_case, test_case.test_run.release)

    def ingest_api_check_failure(self, api_check_result_id: str, release_id: str = None) -> ErrorEvent:
        """Ingest error from failed API check."""
        api_check_result = ApiCheckResult.objects.select_related('api_check', 'api_check__project', 'api_check__environment').get(id=api_check_result_id)
        if api_check_result.is_success:
            raise ValueError('API check result is not a failure')

        release = None
        if release_id:
            release = Release.objects.get(id=release_id)

        return self.grouping_service.process_api_check_failure(api_check_result, release)

    def ingest_manual_error(
        self,
        project,
        fingerprint: str,
        exception_class: str,
        message: str,
        traceback: str,
        context: dict = None,
        release: Release = None,
        environment=None,
    ) -> ErrorEvent:
        """Ingest manually reported error."""
        return self.grouping_service._create_error_event(
            project=project,
            fingerprint=fingerprint,
            exception_class=exception_class,
            message=message,
            traceback=traceback,
            source=ErrorEvent.Source.MANUAL,
            source_id='manual',
            context=context or {},
            release=release,
            environment=environment,
        )