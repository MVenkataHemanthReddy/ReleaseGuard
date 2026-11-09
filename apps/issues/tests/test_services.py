"""
Tests for Issue Grouping services.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone

from apps.issues.models import IssueGroup, ErrorEvent
from apps.issues.services import IssueGroupingService, IssueGroupService, ErrorEventIngestionService
from apps.releases.models import Release, TestRun, TestCaseResult
from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.projects.models import Project, Environment
from apps.organizations.models import Organisation
from apps.accounts.models import User


# ==================== Fixtures ====================

@pytest.fixture
def user(db):
    return User.objects.create_user(email='test@example.com', full_name='Test User', password='pass123')


@pytest.fixture
def organisation(db, user):
    org = Organisation.objects.create(name='Test Org', slug='test-org')
    org.memberships.create(user=user, role='OWNER')
    return org


@pytest.fixture
def project(db, organisation):
    return Project.objects.create(organisation=organisation, name='Test Project', slug='test-project')


@pytest.fixture
def environment(db, project):
    return Environment.objects.create(project=project, name='staging', type='staging', is_default=True)


@pytest.fixture
def release(db, project, environment):
    return Release.objects.create(
        project=project,
        environment=environment,
        version='1.0.0',
        commit_sha='a' * 40,
        branch='main',
        workflow_run_id='run_123',
        deployed_at=timezone.now(),
    )


@pytest.fixture
def test_run(db, release):
    return TestRun.objects.create(
        release=release,
        name='unit',
        status=TestRun.Status.COMPLETED,
        total_tests=10,
        passed_tests=9,
        failed_tests=1,
        idempotency_key='run_123:unit',
    )


@pytest.fixture
def failed_test_case(db, test_run):
    return TestCaseResult.objects.create(
        test_run=test_run,
        classname='test_api',
        name='test_login',
        status=TestCaseResult.Status.FAILED,
        message='AssertionError: Expected 200, got 401',
        traceback='File "test_api.py", line 10\n    assert response.status_code == 200',
        fingerprint='abc123fingerprint',
    )


@pytest.fixture
def api_check(db, project, environment):
    return ApiCheck.objects.create(
        project=project,
        environment=environment,
        name='Health Check',
        url='https://api.example.com/health',
        method='GET',
        expected_status=200,
        timeout_seconds=10,
        interval_seconds=300,
        is_active=True,
    )


@pytest.fixture
def failed_api_check_result(db, api_check):
    return ApiCheckResult.objects.create(
        api_check=api_check,
        status=ApiCheckResult.Status.FAILURE,
        status_code=500,
        error_message='Internal Server Error',
        error_type='ServerError',
        latency_ms=100,
        triggered_by='scheduled',
    )


# ==================== IssueGroupingService Tests ====================

class TestIssueGroupingService:
    """Tests for IssueGroupingService."""

    def test_process_test_failure_creates_issue_group(self, release, failed_test_case):
        """Processing test failure creates IssueGroup and ErrorEvent."""
        service = IssueGroupingService()
        error_event = service.process_test_failure(failed_test_case, release)

        assert error_event.id is not None
        assert error_event.issue_group is not None
        assert error_event.source == ErrorEvent.Source.TEST_FAILURE
        assert error_event.fingerprint == failed_test_case.fingerprint

        # Issue group should be created
        issue_group = error_event.issue_group
        assert issue_group.project == release.project
        assert issue_group.fingerprint == failed_test_case.fingerprint
        assert issue_group.occurrence_count == 1
        assert issue_group.status == IssueGroup.Status.OPEN

    def test_process_test_failure_same_fingerprint_increments(self, release, test_run):
        """Same fingerprint should increment existing issue group."""
        service = IssueGroupingService()

        # Create first failure
        tc1 = TestCaseResult.objects.create(
            test_run=test_run,
            classname='test_api',
            name='test_login',
            status=TestCaseResult.Status.FAILED,
            fingerprint='same_fingerprint',
        )
        event1 = service.process_test_failure(tc1, release)
        group1 = event1.issue_group

        # Create second failure with same fingerprint
        tc2 = TestCaseResult.objects.create(
            test_run=test_run,
            classname='test_api',
            name='test_login',  # Same test
            status=TestCaseResult.Status.FAILED,
            fingerprint='same_fingerprint',
        )
        event2 = service.process_test_failure(tc2, release)

        # Should be same issue group
        assert event2.issue_group.id == group1.id
        assert event2.issue_group.occurrence_count == 2

    def test_process_api_check_failure(self, failed_api_check_result, project):
        """Processing API check failure creates IssueGroup and ErrorEvent."""
        service = IssueGroupingService()
        error_event = service.process_api_check_failure(failed_api_check_result)

        assert error_event.id is not None
        assert error_event.issue_group is not None
        assert error_event.source == ErrorEvent.Source.API_CHECK
        assert error_event.fingerprint != ''

        issue_group = error_event.issue_group
        assert issue_group.project == project
        assert issue_group.occurrence_count == 1

    def test_process_api_check_failure_with_release(self, failed_api_check_result, release):
        """Processing API check failure with release links to release."""
        service = IssueGroupingService()
        error_event = service.process_api_check_failure(failed_api_check_result, release=release)

        assert error_event.release == release
        assert error_event.issue_group.last_seen_release == release


# ==================== IssueGroupService Tests ====================

class TestIssueGroupService:
    """Tests for IssueGroupService."""

    @pytest.fixture
    def issue_group(self, project):
        return IssueGroup.objects.create(
            project=project,
            fingerprint='test_fp',
            title='Test Error',
            description='Test description',
            error_type='test_failure',
            exception_class='AssertionError',
        )

    def test_update_status(self, issue_group, user):
        """Update issue group status."""
        service = IssueGroupService()

        # Open -> In Progress
        updated = service.update_status(issue_group, IssueGroup.Status.IN_PROGRESS, user=user)
        assert updated.status == IssueGroup.Status.IN_PROGRESS
        assert updated.assigned_to == user

        # In Progress -> Resolved
        updated = service.update_status(issue_group, IssueGroup.Status.RESOLVED, user=user)
        assert updated.status == IssueGroup.Status.RESOLVED
        assert updated.assigned_to == user

    def test_update_status_invalid_transition(self, issue_group):
        """Invalid status transition should raise error."""
        service = IssueGroupService()

        # Open -> Resolved is valid
        service.update_status(issue_group, IssueGroup.Status.RESOLVED)

        # Resolved -> In Progress is invalid
        with pytest.raises(ValueError, match='Cannot transition'):
            service.update_status(issue_group, IssueGroup.Status.IN_PROGRESS)

    def test_mark_regression(self, issue_group):
        """Mark issue group as regression."""
        service = IssueGroupService()

        assert issue_group.is_regression is False
        service.mark_regression(issue_group)
        issue_group.refresh_from_db()
        assert issue_group.is_regression is True

        # Calling again should not change
        service.mark_regression(issue_group)
        issue_group.refresh_from_db()
        assert issue_group.is_regression is True

    def test_assign(self, issue_group, user):
        """Assign issue group to user."""
        service = IssueGroupService()

        service.assign(issue_group, user)
        issue_group.refresh_from_db()
        assert issue_group.assigned_to == user
        assert issue_group.status == IssueGroup.Status.IN_PROGRESS

    def test_add_tags(self, issue_group):
        """Add tags to issue group."""
        service = IssueGroupService()

        service.add_tags(issue_group, {'severity': 'high', 'team': 'backend'})
        issue_group.refresh_from_db()
        assert issue_group.tags == {'severity': 'high', 'team': 'backend'}

        # Adding more tags should merge
        service.add_tags(issue_group, {'component': 'auth'})
        issue_group.refresh_from_db()
        assert issue_group.tags == {'severity': 'high', 'team': 'backend', 'component': 'auth'}


# ==================== ErrorEventIngestionService Tests ====================

class TestErrorEventIngestionService:
    """Tests for ErrorEventIngestionService."""

    def test_ingest_test_failure(self, failed_test_case, release):
        """Ingest test failure by ID."""
        service = ErrorEventIngestionService()
        error_event = service.ingest_test_failure(str(failed_test_case.id))

        assert error_event.id is not None
        # ErrorEvent doesn't have direct test_case FK, check source_id instead
        assert error_event.source_id == str(failed_test_case.id)

    def test_ingest_test_failure_not_failed(self, test_run):
        """Ingesting non-failed test should raise error."""
        passed_test = TestCaseResult.objects.create(
            test_run=test_run,
            classname='test_pass',
            name='test_pass',
            status=TestCaseResult.Status.PASSED,
        )

        service = ErrorEventIngestionService()
        with pytest.raises(ValueError, match='not a failure'):
            service.ingest_test_failure(str(passed_test.id))

    def test_ingest_api_check_failure(self, failed_api_check_result):
        """Ingest API check failure by ID."""
        service = ErrorEventIngestionService()
        error_event = service.ingest_api_check_failure(str(failed_api_check_result.id))

        assert error_event.id is not None
        # ErrorEvent doesn't have direct api_check_result FK, check source_id instead
        assert error_event.source_id == str(failed_api_check_result.id)

    def test_ingest_api_check_failure_with_release(self, failed_api_check_result, release):
        """Ingest API check failure with release."""
        service = ErrorEventIngestionService()
        error_event = service.ingest_api_check_failure(
            str(failed_api_check_result.id),
            release_id=str(release.id),
        )

        assert error_event.release == release

    def test_ingest_api_check_failure_not_failed(self, api_check):
        """Ingesting successful API check should raise error."""
        success_result = ApiCheckResult.objects.create(
            api_check=api_check,
            status=ApiCheckResult.Status.SUCCESS,
            status_code=200,
            triggered_by='scheduled',
        )

        service = ErrorEventIngestionService()
        with pytest.raises(ValueError, match='not a failure'):
            service.ingest_api_check_failure(str(success_result.id))

    def test_ingest_manual_error(self, project):
        """Ingest manually reported error."""
        service = ErrorEventIngestionService()
        error_event = service.ingest_manual_error(
            project=project,
            fingerprint='manual_fp',
            exception_class='ManualError',
            message='Something went wrong',
            traceback='Traceback...',
            context={'custom': 'data'},
        )

        assert error_event.id is not None
        assert error_event.source == ErrorEvent.Source.MANUAL
        assert error_event.issue_group.fingerprint == 'manual_fp'


# Run with: pytest apps/issues/tests/test_services.py -v