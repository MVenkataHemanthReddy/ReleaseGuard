"""
Tests for API Check services.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta

from django.utils import timezone
from django.db import models

from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.api_checks.services import ApiCheckService, ApiCheckScheduler
from apps.api_checks.security import SSRFError
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


class TestApiCheckService:
    """Tests for ApiCheckService."""

    @pytest.fixture
    def api_check(self, project, environment):
        """Create an API check for testing."""
        return ApiCheck.objects.create(
            project=project,
            environment=environment,
            name='Test API Check',
            url='https://api.example.com/health',
            method='GET',
            expected_status=200,
            timeout_seconds=10,
            interval_seconds=300,
            is_active=True,
            is_critical=False,
        )

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_success(self, mock_request, api_check):
        """Successful check should return SUCCESS status."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'OK'
        mock_response.content = b'OK'
        mock_response.headers = {'Content-Type': 'text/plain'}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check(triggered_by='manual')

        assert result.status == ApiCheckResult.Status.SUCCESS
        assert result.status_code == 200
        assert result.content_match is None  # No expected content set
        assert result.ssl_valid is not None  # Should validate SSL for HTTPS

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_wrong_status(self, mock_request, api_check):
        """Wrong status code should return FAILURE."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_response.content = b'Internal Server Error'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.status == ApiCheckResult.Status.FAILURE
        assert result.status_code == 500

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_content_match(self, mock_request, api_check):
        """Content validation should work."""
        api_check.expected_content = 'healthy'
        api_check.save()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'System is healthy'
        mock_response.content = b'System is healthy'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.content_match is True
        assert result.status == ApiCheckResult.Status.SUCCESS

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_content_mismatch(self, mock_request, api_check):
        """Content mismatch should be FAILURE."""
        api_check.expected_content = 'healthy'
        api_check.save()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'System is broken'
        mock_response.content = b'System is broken'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.content_match is False
        assert result.status == ApiCheckResult.Status.FAILURE

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_timeout(self, mock_request, api_check):
        """Timeout should return TIMEOUT status."""
        import requests
        mock_request.side_effect = requests.Timeout()

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.status == ApiCheckResult.Status.TIMEOUT
        assert 'timed out' in result.error_message

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_ssrf_error(self, mock_request, api_check):
        """SSRF error should return ERROR status."""
        mock_request.side_effect = SSRFError('URL blocked: private IP')

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.status == ApiCheckResult.Status.ERROR
        assert result.error_type == 'SSRFError'
        assert 'blocked' in result.error_message

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_generic_error(self, mock_request, api_check):
        """Generic exception should return ERROR status."""
        mock_request.side_effect = Exception('Connection refused')

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.status == ApiCheckResult.Status.ERROR
        assert result.error_type == 'Exception'
        assert 'Connection refused' in result.error_message

    @patch('apps.api_checks.services.make_safe_request')
    @patch('apps.api_checks.services.time.perf_counter')
    def test_run_check_stores_timing(self, mock_perf_counter, mock_request, api_check):
        """Result should include timing breakdown."""
        # Mock perf_counter to return increasing values
        # Called 4 times: run_check start, _execute_request request_start, 
        # _execute_request end, run_check end
        mock_perf_counter.side_effect = [1000.0, 1000.0, 1000.5, 1000.5]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'OK'
        mock_response.content = b'OK'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check()

        assert result.latency_ms is not None
        assert result.latency_ms == 500  # 1000.5 - 1000.0 = 0.5s = 500ms

    @patch('apps.api_checks.services.make_safe_request')
    def test_run_check_idempotency_key(self, mock_request, api_check):
        """Idempotency key should be stored."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'OK'
        mock_response.content = b'OK'
        mock_response.headers = {}

        mock_request.return_value = mock_response

        service = ApiCheckService(api_check)
        result = service.run_check(idempotency_key='test-key-123')

        assert result.idempotency_key == 'test-key-123'


class TestApiCheckScheduler:
    """Tests for ApiCheckScheduler."""

    @pytest.fixture
    def active_check(self, project, environment):
        return ApiCheck.objects.create(
            project=project,
            environment=environment,
            name='Active Check',
            url='https://api.example.com/health',
            interval_seconds=60,
            is_active=True,
        )

    @pytest.fixture
    def inactive_check(self, project, environment):
        return ApiCheck.objects.create(
            project=project,
            environment=environment,
            name='Inactive Check',
            url='https://api.example.com/health',
            interval_seconds=60,
            is_active=False,
        )

    @pytest.fixture
    def due_check(self, project, environment):
        """Check that's due to run."""
        check = ApiCheck.objects.create(
            project=project,
            environment=environment,
            name='Due Check',
            url='https://api.example.com/health',
            interval_seconds=60,
            is_active=True,
        )
        # Set last_run_at to 2 minutes ago (interval is 60s)
        check.last_run_at = timezone.now() - timedelta(minutes=2)
        check.save()
        return check

    @pytest.fixture
    def not_due_check(self, project, environment):
        """Check that's not due yet."""
        check = ApiCheck.objects.create(
            project=project,
            environment=environment,
            name='Not Due Check',
            url='https://api.example.com/health',
            interval_seconds=60,
            is_active=True,
        )
        # Set last_run_at to 30 seconds ago
        check.last_run_at = timezone.now() - timedelta(seconds=30)
        check.save()
        return check

    def test_schedule_due_checks_queues_due(self, due_check, not_due_check, inactive_check):
        """Only due active checks should be queued."""
        from apps.core.models import BackgroundJob

        # Clear any existing jobs
        BackgroundJob.objects.all().delete()

        queued = ApiCheckScheduler.schedule_due_checks()

        assert queued == 1

        job = BackgroundJob.objects.first()
        assert job.name == 'run_api_check'
        assert job.payload['api_check_id'] == str(due_check.id)
        assert job.payload['triggered_by'] == 'scheduled'

    def test_schedule_due_checks_idempotent(self, due_check):
        """Calling twice should not create duplicate jobs."""
        from apps.core.models import BackgroundJob

        BackgroundJob.objects.all().delete()

        ApiCheckScheduler.schedule_due_checks()
        queued1 = ApiCheckScheduler.schedule_due_checks()

        assert queued1 == 0  # Second call should queue nothing

        assert BackgroundJob.objects.count() == 1


# Run with: pytest apps/api_checks/tests/test_services.py -v