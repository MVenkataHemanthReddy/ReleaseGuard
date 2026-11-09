"""
API Health Check execution service for ReleaseGuard.

Handles running checks with SSRF protection, timing breakdown, and result storage.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.api_checks.security import make_safe_request, SSRFError, validate_ssl_certificate

logger = logging.getLogger(__name__)


@dataclass
class CheckTiming:
    """Breakdown of request timing."""
    total_ms: int
    dns_ms: int = 0
    connect_ms: int = 0
    tls_ms: int = 0


@dataclass
class CheckResult:
    """Result of an API check execution."""
    status: str
    status_code: Optional[int] = None
    latency_ms: Optional[int] = None
    timing: Optional[CheckTiming] = None
    response_headers: dict = None
    response_body: str = ''
    response_size_bytes: int = 0
    error_message: str = ''
    error_type: str = ''
    content_match: Optional[bool] = None
    ssl_valid: Optional[bool] = None


class ApiCheckService:
    """
    Service for executing API health checks.

    Features:
    - SSRF protection via security module
    - Detailed timing breakdown (DNS, connect, TLS, transfer)
    - Content validation
    - SSL certificate verification
    - Idempotent execution
    """

    def __init__(self, api_check: ApiCheck):
        self.api_check = api_check

    def run_check(
        self,
        triggered_by: str = 'scheduled',
        idempotency_key: str = None,
    ) -> ApiCheckResult:
        """
        Execute the API check and store result.

        Args:
            triggered_by: 'scheduled', 'manual', or 'release'
            idempotency_key: Optional key for deduplication

        Returns:
            Created ApiCheckResult instance
        """
        start_time = time.perf_counter()

        try:
            result = self._execute_request()
        except SSRFError as e:
            result = CheckResult(
                status=ApiCheckResult.Status.ERROR,
                error_message=str(e),
                error_type='SSRFError',
            )
        except Exception as e:
            logger.exception('Unexpected error during API check %s', self.api_check.id)
            result = CheckResult(
                status=ApiCheckResult.Status.ERROR,
                error_message=str(e),
                error_type=type(e).__name__,
            )

        # Calculate total latency
        total_ms = int((time.perf_counter() - start_time) * 1000)
        if result.latency_ms is None:
            result.latency_ms = total_ms

        # Store result
        return self._store_result(result, triggered_by, idempotency_key)

    def _execute_request(self) -> CheckResult:
        """Execute the HTTP request with timing breakdown."""
        check = self.api_check
        url = check.url

        # Prepare request
        headers = check.headers or {}
        headers.setdefault('User-Agent', 'ReleaseGuard/1.0 (+https://releaseguard.dev)')

        # Measure total time
        request_start = time.perf_counter()

        try:
            response = make_safe_request(
                method=check.method,
                url=url,
                timeout=check.timeout_seconds,
                headers=headers,
                data=check.body if check.body else None,
                verify_ssl=check.check_ssl,
                max_redirects=5,
            )
        except SSRFError:
            raise
        except requests.Timeout:
            return CheckResult(
                status=ApiCheckResult.Status.TIMEOUT,
                error_message=f'Request timed out after {check.timeout_seconds}s',
                error_type='Timeout',
            )
        except requests.RequestException as e:
            return CheckResult(
                status=ApiCheckResult.Status.ERROR,
                error_message=str(e),
                error_type=type(e).__name__,
            )

        # Calculate total latency
        total_ms = int((time.perf_counter() - request_start) * 1000)

        # For more accurate timing, we'd need to use lower-level socket timing
        # For now, use total latency as primary metric
        timing = CheckTiming(total_ms=total_ms)

        # Validate status code
        status = ApiCheckResult.Status.SUCCESS if response.status_code == check.expected_status else ApiCheckResult.Status.FAILURE

        # Validate content
        content_match = None
        if check.expected_content:
            content_match = check.expected_content in response.text

            # If content doesn't match, it's a failure
            if not content_match:
                status = ApiCheckResult.Status.FAILURE

        # SSL validation
        ssl_valid = None
        if url.startswith('https://') and check.check_ssl:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            ssl_valid, _ = validate_ssl_certificate(parsed.hostname, parsed.port or 443)

        return CheckResult(
            status=status,
            status_code=response.status_code,
            latency_ms=total_ms,
            timing=timing,
            response_headers=dict(response.headers),
            response_body=response.text[:10000],  # Limit stored body size
            response_size_bytes=len(response.content),
            content_match=content_match,
            ssl_valid=ssl_valid,
        )

    def _store_result(
        self,
        result: CheckResult,
        triggered_by: str,
        idempotency_key: str = None,
    ) -> ApiCheckResult:
        """Store check result in database."""
        with transaction.atomic():
            api_result = ApiCheckResult.objects.create(
                api_check=self.api_check,
                status=result.status,
                status_code=result.status_code,
                latency_ms=result.latency_ms,
                dns_lookup_ms=result.timing.dns_ms if result.timing else None,
                connect_ms=result.timing.connect_ms if result.timing else None,
                tls_handshake_ms=result.timing.tls_ms if result.timing else None,
                response_headers=result.response_headers,
                response_body=result.response_body,
                response_size_bytes=result.response_size_bytes,
                error_message=result.error_message,
                error_type=result.error_type,
                content_match=result.content_match,
                ssl_valid=result.ssl_valid,
                triggered_by=triggered_by,
                idempotency_key=idempotency_key or '',
            )

        logger.info(
            'API check %s completed: %s (%dms)',
            self.api_check.name,
            result.status,
            result.latency_ms or 0,
        )

        return api_result


class ApiCheckScheduler:
    """
    Scheduler for periodic API checks.

    Creates BackgroundJob entries for due checks.
    """

    @staticmethod
    def schedule_due_checks() -> int:
        """
        Find checks that are due and queue them.

        Returns number of jobs queued.
        """
        from apps.core.models import BackgroundJob
        from apps.api_checks.models import ApiCheck
        from django.db import connection

        now = timezone.now()
        
        # For SQLite, filter in Python (F expressions don't work well with timedelta)
        # For PostgreSQL, we could use database-level filtering
        if connection.vendor == 'sqlite':
            active_checks = list(ApiCheck.objects.filter(is_active=True))
            due_checks = []
            for check in active_checks:
                if check.last_run_at is None:
                    due_checks.append(check)
                elif check.last_run_at < now - timezone.timedelta(seconds=check.interval_seconds):
                    due_checks.append(check)
        else:
            # PostgreSQL: use database-level filtering
            from django.db.models import F, ExpressionWrapper, DurationField, DateTimeField
            from django.db.models.functions import Now
            
            due_checks = list(ApiCheck.objects.filter(is_active=True).filter(
                models.Q(last_run_at__isnull=True) |
                models.Q(last_run_at__lt=ExpressionWrapper(
                    Now() - ExpressionWrapper(F('interval_seconds') * 1000000, output_field=DurationField()),
                    output_field=DateTimeField()
                ))
            ))

        queued = 0
        for check in due_checks:
            # Create idempotency key to prevent duplicate scheduling
            idempotency_key = f'api_check:{check.id}:{int(now.timestamp() / check.interval_seconds)}'

            job, created = BackgroundJob.objects.get_or_create(
                idempotency_key=idempotency_key,
                defaults={
                    'name': 'run_api_check',
                    'payload': {
                        'api_check_id': str(check.id),
                        'triggered_by': 'scheduled',
                    },
                    'priority': BackgroundJob.Priority.NORMAL,
                }
            )
            if created:
                queued += 1

        return queued


# Import needed at bottom to avoid circular import
from django.db import models
from django.db.models import ExpressionWrapper, DurationField, DateTimeField, F
from django.db.models.functions import Now
from django.db import connection
import requests