"""
API Health Check models for ReleaseGuard.

Stores HTTP/HTTPS endpoint checks with status, latency, and history.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel, UUIDTimeStampedModel
from apps.projects.models import Project, Environment


class ApiCheck(UUIDTimeStampedSoftDeleteModel):
    """
    An API health check configuration.

    Defines an endpoint to monitor, expected response, and check frequency.
    """

    class Type(models.TextChoices):
        HTTP = 'http', _('HTTP')
        HTTPS = 'https', _('HTTPS')

    class Method(models.TextChoices):
        GET = 'GET', _('GET')
        POST = 'POST', _('POST')
        HEAD = 'HEAD', _('HEAD')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='api_checks',
        verbose_name=_('project'),
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='api_checks',
        verbose_name=_('environment'),
        null=True,
        blank=True,
        help_text=_('Optional: limit check to specific environment'),
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    # Endpoint configuration
    url = models.URLField(_('URL'), max_length=2048)
    method = models.CharField(
        _('method'),
        max_length=10,
        choices=Method.choices,
        default=Method.GET,
    )
    expected_status = models.PositiveIntegerField(
        _('expected status'),
        default=200,
        help_text=_('Expected HTTP status code'),
    )
    timeout_seconds = models.PositiveIntegerField(
        _('timeout (seconds)'),
        default=10,
        help_text=_('Request timeout in seconds'),
    )
    headers = models.JSONField(_('headers'), default=dict, blank=True)
    body = models.TextField(_('request body'), blank=True)

    # Validation
    expected_content = models.TextField(
        _('expected content'),
        blank=True,
        help_text=_('Substring that must appear in response body'),
    )
    check_ssl = models.BooleanField(_('verify SSL'), default=True)

    # Scheduling
    interval_seconds = models.PositiveIntegerField(
        _('interval (seconds)'),
        default=300,
        help_text=_('How often to run this check'),
    )
    is_active = models.BooleanField(_('active'), default=True)

    # Criticality for release policy
    is_critical = models.BooleanField(
        _('critical'),
        default=False,
        help_text=_('If true, failure affects release policy (blocking)'),
    )

    # Scheduling
    last_run_at = models.DateTimeField(_('last run at'), null=True, blank=True)

    class Meta:
        verbose_name = _('API check')
        verbose_name_plural = _('API checks')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_api_check_name_per_project',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['environment', 'is_active']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.name}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('api-checks:detail', kwargs={'pk': self.pk})


class ApiCheckResult(UUIDTimeStampedModel):
    """
    Result of a single API check execution.

    Stores status, latency, response details, and any error.
    """

    class Status(models.TextChoices):
        SUCCESS = 'success', _('Success')
        FAILURE = 'failure', _('Failure')
        TIMEOUT = 'timeout', _('Timeout')
        ERROR = 'error', _('Error')

    api_check = models.ForeignKey(
        ApiCheck,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name=_('API check'),
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        db_index=True,
    )

    # Timing
    latency_ms = models.PositiveIntegerField(
        _('latency (ms)'),
        null=True,
        blank=True,
        help_text=_('Response time in milliseconds'),
    )
    dns_lookup_ms = models.PositiveIntegerField(
        _('DNS lookup (ms)'),
        null=True,
        blank=True,
    )
    connect_ms = models.PositiveIntegerField(
        _('connect (ms)'),
        null=True,
        blank=True,
    )
    tls_handshake_ms = models.PositiveIntegerField(
        _('TLS handshake (ms)'),
        null=True,
        blank=True,
    )

    # Response
    status_code = models.PositiveIntegerField(_('status code'), null=True, blank=True)
    response_headers = models.JSONField(_('response headers'), default=dict, blank=True, null=True)
    response_body = models.TextField(_('response body'), blank=True)
    response_size_bytes = models.PositiveIntegerField(_('response size (bytes)'), default=0)

    # Error details
    error_message = models.TextField(_('error message'), blank=True)
    error_type = models.CharField(_('error type'), max_length=100, blank=True)

    # Validation
    content_match = models.BooleanField(_('content match'), null=True, blank=True)
    ssl_valid = models.BooleanField(_('SSL valid'), null=True, blank=True)

    # Idempotency
    triggered_by = models.CharField(
        _('triggered by'),
        max_length=50,
        choices=[
            ('scheduled', _('Scheduled')),
            ('manual', _('Manual')),
            ('release', _('Release deployment')),
        ],
        default='scheduled',
    )
    idempotency_key = models.CharField(_('idempotency key'), max_length=255, blank=True, db_index=True)

    class Meta:
        verbose_name = _('API check result')
        verbose_name_plural = _('API check results')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_check', 'status', 'created_at']),
            models.Index(fields=['idempotency_key']),
        ]

    def __str__(self):
        return f'{self.api_check.name} [{self.status}] at {self.created_at}'

    @property
    def is_success(self):
        return self.status == self.Status.SUCCESS

    @property
    def total_latency_ms(self):
        """Sum of all timing components."""
        parts = [
            self.dns_lookup_ms or 0,
            self.connect_ms or 0,
            self.tls_handshake_ms or 0,
            (self.latency_ms or 0) - (self.dns_lookup_ms or 0) - (self.connect_ms or 0) - (self.tls_handshake_ms or 0),
        ]
        return sum(p for p in parts if p > 0) or self.latency_ms or 0