"""
Release, TestRun, TestCaseResult, and ReleaseAnalysis models for ReleaseGuard.

Core domain models for the ingestion and analysis pipeline.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel
from apps.projects.models import Project, Environment


class Release(UUIDTimeStampedSoftDeleteModel):
    """
    A software release deployed to an environment.

    Identified by version, commit SHA, branch, and workflow run.
    Scoped to project and environment.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='releases',
        verbose_name=_('project'),
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='releases',
        verbose_name=_('environment'),
    )
    version = models.CharField(_('version'), max_length=255, help_text=_('SemVer, tag, or build number'))
    commit_sha = models.CharField(_('commit SHA'), max_length=64, db_index=True)
    commit_short_sha = models.CharField(_('short SHA'), max_length=12, db_index=True)
    branch = models.CharField(_('branch'), max_length=255, db_index=True)
    workflow_run_id = models.CharField(_('workflow run ID'), max_length=100, db_index=True, help_text=_('CI workflow run identifier (e.g., GitHub Actions run_id)'))
    workflow_run_url = models.URLField(_('workflow run URL'), blank=True)
    commit_message = models.TextField(_('commit message'), blank=True)
    commit_author = models.CharField(_('commit author'), max_length=255, blank=True)
    commit_timestamp = models.DateTimeField(_('commit timestamp'), null=True, blank=True)
    deployed_at = models.DateTimeField(_('deployed at'), null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _('release')
        verbose_name_plural = _('releases')
        ordering = ['-deployed_at', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'workflow_run_id'],
                name='unique_release_per_workflow_run',
            ),
            models.UniqueConstraint(
                fields=['project', 'environment', 'version'],
                name='unique_version_per_project_environment',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'environment', 'deployed_at']),
            models.Index(fields=['project', 'commit_sha']),
            models.Index(fields=['project', 'branch', 'deployed_at']),
        ]

    def __str__(self):
        return f'{self.project.name} @ {self.version} ({self.environment.name})'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('releases:detail', kwargs={'pk': self.pk})

    @property
    def previous_release(self):
        """Get the previous release in the same project+environment."""
        if not self.environment or not self.deployed_at:
            return None
        return Release.objects.filter(
            project=self.project,
            environment=self.environment,
            deployed_at__lt=self.deployed_at,
        ).order_by('-deployed_at').first()


class TestRun(UUIDTimeStampedSoftDeleteModel):
    """
    A test execution (CI run) associated with a release.

    Contains summary metrics and links to individual test case results.
    One release can have multiple test runs (e.g., unit, integration, e2e).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name='test_runs',
        verbose_name=_('release'),
    )
    name = models.CharField(_('name'), max_length=255, default='default', help_text=_('Test suite name, e.g., "unit", "integration"'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    # Summary metrics (denormalized for dashboard performance)
    total_tests = models.PositiveIntegerField(_('total tests'), default=0)
    passed_tests = models.PositiveIntegerField(_('passed tests'), default=0)
    failed_tests = models.PositiveIntegerField(_('failed tests'), default=0)
    skipped_tests = models.PositiveIntegerField(_('skipped tests'), default=0)
    error_tests = models.PositiveIntegerField(_('error tests'), default=0)
    total_duration = models.FloatField(_('total duration (seconds)'), default=0.0)

    # Raw report storage (optional, for debugging)
    raw_xml = models.TextField(_('raw XML'), blank=True)
    xml_size = models.PositiveIntegerField(_('XML size (bytes)'), default=0)

    # Idempotency
    idempotency_key = models.CharField(_('idempotency key'), max_length=255, db_index=True, help_text=_('Unique key for deduplication (e.g., workflow_run_id + test_suite)'))

    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    finished_at = models.DateTimeField(_('finished at'), null=True, blank=True)

    class Meta:
        verbose_name = _('test run')
        verbose_name_plural = _('test runs')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['release', 'idempotency_key'],
                name='unique_test_run_per_release_idempotency',
            ),
        ]
        indexes = [
            models.Index(fields=['release', 'name', 'status']),
            models.Index(fields=['idempotency_key']),
        ]

    def __str__(self):
        return f'{self.release} / {self.name} ({self.status})'

    @property
    def pass_rate(self):
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def failure_rate(self):
        if self.total_tests == 0:
            return 0.0
        return ((self.failed_tests + self.error_tests) / self.total_tests) * 100


class TestCaseResult(UUIDTimeStampedSoftDeleteModel):
    """
    Individual test case result within a TestRun.

    Each row represents one test method/class execution.
    """

    class Status(models.TextChoices):
        PASSED = 'passed', _('Passed')
        FAILED = 'failed', _('Failed')
        SKIPPED = 'skipped', _('Skipped')
        ERROR = 'error', _('Error')
        XFAIL = 'xfail', _('Expected Fail')
        XPASS = 'xpass', _('Unexpected Pass')

    test_run = models.ForeignKey(
        TestRun,
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name=_('test run'),
    )
    # JUnit identifies tests by classname + name
    classname = models.CharField(_('class name'), max_length=512, db_index=True)
    name = models.CharField(_('test name'), max_length=512, db_index=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, db_index=True)
    duration = models.FloatField(_('duration (seconds)'), default=0.0)

    # Failure/error details
    message = models.TextField(_('message'), blank=True)
    output = models.TextField(_('output (stdout/stderr)'), blank=True)
    traceback = models.TextField(_('traceback'), blank=True)

    # Fingerprint for error grouping (computed later)
    fingerprint = models.CharField(_('fingerprint'), max_length=64, blank=True, db_index=True)

    # JUnit properties (flexible key-value)
    properties = models.JSONField(_('properties'), default=dict, blank=True)

    class Meta:
        verbose_name = _('test case result')
        verbose_name_plural = _('test case results')
        ordering = ['classname', 'name']
        indexes = [
            models.Index(fields=['test_run', 'status']),
            models.Index(fields=['test_run', 'classname', 'name']),
            models.Index(fields=['fingerprint']),
        ]

    def __str__(self):
        return f'{self.classname}.{self.name} [{self.status}]'

    @property
    def test_identifier(self):
        """Unique identifier for this test within a project (for comparison)."""
        return f'{self.classname}.{self.name}'

    @property
    def is_failure(self):
        return self.status in (self.Status.FAILED, self.Status.ERROR)

    @property
    def is_passed(self):
        return self.status == self.Status.PASSED


class ReleaseAnalysis(UUIDTimeStampedSoftDeleteModel):
    """
    Deterministic policy evaluation result for a release.

    Stores GREEN/YELLOW/RED status with rule-by-rule explanation.
    One analysis per release (created after test runs processed).
    """

    class Status(models.TextChoices):
        GREEN = 'green', _('Green')
        YELLOW = 'yellow', _('Yellow')
        RED = 'red', _('Red')
        PENDING = 'pending', _('Pending')

    release = models.OneToOneField(
        Release,
        on_delete=models.CASCADE,
        related_name='analysis',
        verbose_name=_('release'),
    )
    status = models.CharField(_('status'), max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    policy_version = models.CharField(_('policy version'), max_length=50, default='1.0')

    # Rule evaluation results (JSON for flexibility)
    rule_results = models.JSONField(_('rule results'), default=list, help_text=_('List of {rule, passed, message, details}'))

    # Summary counts
    new_failures = models.PositiveIntegerField(_('new failures'), default=0)
    persistent_failures = models.PositiveIntegerField(_('persistent failures'), default=0)
    fixed_failures = models.PositiveIntegerField(_('fixed failures'), default=0)
    flaky_tests = models.PositiveIntegerField(_('flaky tests'), default=0)

    # Comparison reference
    compared_to_release = models.ForeignKey(
        Release,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyses_as_baseline',
        verbose_name=_('compared to release'),
    )

    evaluated_at = models.DateTimeField(_('evaluated at'), null=True, blank=True)

    class Meta:
        verbose_name = _('release analysis')
        verbose_name_plural = _('release analyses')
        ordering = ['-evaluated_at', '-created_at']
        indexes = [
            models.Index(fields=['release', 'status']),
            models.Index(fields=['status', 'evaluated_at']),
        ]

    def __str__(self):
        return f'{self.release} → {self.get_status_display()}'

    def get_failed_rules(self):
        """Return rules that failed (caused non-GREEN status)."""
        return [r for r in self.rule_results if not r.get('passed', True)]

    def get_warning_rules(self):
        """Return rules that passed but have warnings."""
        return [r for r in self.rule_results if r.get('passed', True) and r.get('warning')]