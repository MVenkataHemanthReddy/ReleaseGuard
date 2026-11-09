"""
Issue Group and Error Event models for ReleaseGuard.

Error events are individual occurrences of errors (from test failures, API check failures, etc.).
Issue groups cluster related error events by fingerprint for deduplication and tracking.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel
from apps.projects.models import Project, Environment
from apps.releases.models import Release


class IssueGroup(UUIDTimeStampedSoftDeleteModel):
    """
    A group of related error events sharing the same fingerprint.

    Represents a unique error pattern that can occur across releases,
    environments, and test runs.
    """

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        IGNORED = 'ignored', _('Ignored')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='issue_groups',
        verbose_name=_('project'),
    )
    fingerprint = models.CharField(_('fingerprint'), max_length=64, db_index=True)
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    # Classification
    error_type = models.CharField(_('error type'), max_length=100, blank=True)
    exception_class = models.CharField(_('exception class'), max_length=255, blank=True)

    # Status tracking
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    is_regression = models.BooleanField(_('is regression'), default=False)

    # Occurrence tracking
    first_seen_at = models.DateTimeField(_('first seen at'), default=timezone.now, db_index=True)
    last_seen_at = models.DateTimeField(_('last seen at'), default=timezone.now, db_index=True)
    occurrence_count = models.PositiveIntegerField(_('occurrence count'), default=1)

    # Release context
    first_seen_release = models.ForeignKey(
        Release,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='first_seen_issues',
        verbose_name=_('first seen release'),
    )
    last_seen_release = models.ForeignKey(
        Release,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_seen_issues',
        verbose_name=_('last seen release'),
    )

    # Assignment
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        verbose_name=_('assigned to'),
    )

    # Metadata
    tags = models.JSONField(_('tags'), default=dict, blank=True)

    class Meta:
        verbose_name = _('issue group')
        verbose_name_plural = _('issue groups')
        ordering = ['-last_seen_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'fingerprint'],
                name='unique_issue_group_per_project_fingerprint',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'status', 'last_seen_at']),
            models.Index(fields=['project', 'is_regression', 'last_seen_at']),
            models.Index(fields=['fingerprint']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.title} ({self.fingerprint[:8]}...)'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('issues:detail', kwargs={'pk': self.pk})

    def increment_occurrence(self, release: Release = None):
        """Increment occurrence count and update timestamps."""
        self.occurrence_count += 1
        self.last_seen_at = timezone.now()
        if release:
            self.last_seen_release = release
        self.save(update_fields=['occurrence_count', 'last_seen_at', 'last_seen_release'])


class ErrorEvent(UUIDTimeStampedSoftDeleteModel):
    """
    A single occurrence of an error.

    Linked to a specific test case result, API check result, or manual report.
    Grouped into IssueGroup by fingerprint.
    """

    class Source(models.TextChoices):
        TEST_FAILURE = 'test_failure', _('Test Failure')
        API_CHECK = 'api_check', _('API Check')
        MANUAL = 'manual', _('Manual Report')

    issue_group = models.ForeignKey(
        IssueGroup,
        on_delete=models.CASCADE,
        related_name='error_events',
        verbose_name=_('issue group'),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='error_events',
        verbose_name=_('project'),
    )
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name='error_events',
        verbose_name=_('release'),
        null=True,
        blank=True,
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='error_events',
        verbose_name=_('environment'),
        null=True,
        blank=True,
    )

    # Source identification
    source = models.CharField(
        _('source'),
        max_length=20,
        choices=Source.choices,
        db_index=True,
    )
    source_id = models.CharField(_('source ID'), max_length=255, blank=True, help_text=_('ID of the source object (test case, API check result, etc.)'))

    # Error details
    fingerprint = models.CharField(_('fingerprint'), max_length=64, db_index=True)
    exception_class = models.CharField(_('exception class'), max_length=255, blank=True)
    message = models.TextField(_('message'), blank=True)
    traceback = models.TextField(_('traceback'), blank=True)

    # Context
    context = models.JSONField(_('context'), default=dict, blank=True, help_text=_('Additional context: test name, URL, request params, etc.'))

    # Timing
    occurred_at = models.DateTimeField(_('occurred at'), default=timezone.now, db_index=True)

    class Meta:
        verbose_name = _('error event')
        verbose_name_plural = _('error events')
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['project', 'source', 'occurred_at']),
            models.Index(fields=['issue_group', 'occurred_at']),
            models.Index(fields=['fingerprint', 'occurred_at']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.exception_class} ({self.fingerprint[:8]}...) at {self.occurred_at}'