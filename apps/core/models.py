"""
Core models for ReleaseGuard.

Provides base model classes used across all apps:
- UUID primary keys
- Timezone-aware timestamps
- Soft delete pattern
- Common utilities
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract base model with created/updated timestamps.

    All models in ReleaseGuard inherit from this (or UUIDTimeStampedModel)
    to have consistent audit fields.
    """

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.

    UUIDs are non-guessable, safe for public URLs/APIs, and don't leak
    information about record counts or creation order.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        verbose_name=_('ID'),
    )

    class Meta:
        abstract = True


class UUIDTimeStampedModel(UUIDModel, TimeStampedModel):
    """
    Combined UUID + timestamp base model.

    This is the standard base for all ReleaseGuard domain models.
    """

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted objects by default.

    Use Model.objects.all_with_deleted() to include soft-deleted records.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft deletes.

    Instead of hard deletion, sets deleted_at timestamp.
    Provides delete() override and restore() method.
    """

    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Access to all records including deleted

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: set deleted_at instead of removing row."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self):
        """Actually delete the row from database. Use sparingly."""
        super().delete()

    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class UUIDTimeStampedSoftDeleteModel(UUIDTimeStampedModel, SoftDeleteModel):
    """
    Full-featured base model: UUID PK + timestamps + soft delete.

    Use this for all primary domain models in ReleaseGuard.
    """

    class Meta:
        abstract = True


class BackgroundJob(UUIDTimeStampedModel):
    """
    PostgreSQL-backed background job queue.

    Jobs are claimed atomically using SELECT FOR UPDATE SKIP LOCKED.
    Supports retries, backoff, and stale job recovery.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CLAIMED = 'claimed', _('Claimed')
        RUNNING = 'running', _('Running')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        DEAD = 'dead', _('Dead (max retries exceeded)')

    class Priority(models.IntegerChoices):
        LOW = 0, _('Low')
        NORMAL = 50, _('Normal')
        HIGH = 100, _('High')
        CRITICAL = 200, _('Critical')

    name = models.CharField(_('job name'), max_length=255, db_index=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    priority = models.IntegerField(_('priority'), choices=Priority.choices, default=Priority.NORMAL)

    # Payload and result
    payload = models.JSONField(_('payload'), default=dict)
    result = models.JSONField(_('result'), default=dict, blank=True)
    error = models.TextField(_('error'), blank=True)

    # Retry configuration
    max_retries = models.PositiveSmallIntegerField(_('max retries'), default=3)
    retry_count = models.PositiveSmallIntegerField(_('retry count'), default=0)
    retry_backoff_seconds = models.PositiveIntegerField(_('retry backoff (seconds)'), default=60)

    # Scheduling
    scheduled_at = models.DateTimeField(_('scheduled at'), null=True, blank=True, db_index=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    # Idempotency (optional unique key to prevent duplicate jobs)
    idempotency_key = models.CharField(_('idempotency key'), max_length=255, blank=True, db_index=True)

    # Worker identification
    worker_id = models.CharField(_('worker ID'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('background job')
        verbose_name_plural = _('background jobs')
        ordering = ['-priority', 'scheduled_at', 'created_at']
        indexes = [
            models.Index(fields=['status', 'priority', 'scheduled_at']),
            models.Index(fields=['idempotency_key']),
        ]

    def __str__(self):
        return f'{self.name} [{self.status}]'

    def can_retry(self):
        return self.retry_count < self.max_retries

    def mark_claimed(self, worker_id):
        self.status = self.Status.CLAIMED
        self.worker_id = worker_id
        self.save(update_fields=['status', 'worker_id'])

    def mark_running(self):
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_completed(self, result=None):
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        if result:
            self.result = result
        self.save(update_fields=['status', 'completed_at', 'result'])

    def mark_failed(self, error, will_retry=True):
        self.error = error
        if will_retry and self.can_retry():
            self.status = self.Status.PENDING
            self.retry_count += 1
            # Schedule retry with exponential backoff
            from django.utils import timezone
            from datetime import timedelta
            self.scheduled_at = timezone.now() + timedelta(seconds=self.retry_backoff_seconds * self.retry_count)
        else:
            self.status = self.Status.DEAD
            self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error', 'retry_count', 'scheduled_at', 'completed_at'])

    @classmethod
    def claim_next_job(cls, worker_id, job_names=None):
        """
        Atomically claim the next pending job for this worker.

        Uses SELECT FOR UPDATE SKIP LOCKED (PostgreSQL) or advisory lock fallback (SQLite).
        Returns claimed job instance or None.
        """
        from django.db import transaction, connection

        queryset = cls.objects.filter(
            status=cls.Status.PENDING,
        ).filter(
            models.Q(scheduled_at__isnull=True) | models.Q(scheduled_at__lte=timezone.now())
        )

        if job_names:
            queryset = queryset.filter(name__in=job_names)

        queryset = queryset.order_by('-priority', 'scheduled_at', 'created_at')

        # Try PostgreSQL-style locking first
        if connection.vendor == 'postgresql':
            with transaction.atomic():
                job = queryset.select_for_update(skip_locked=True).first()
                if job:
                    job.mark_claimed(worker_id)
                    return job
                return None
        else:
            # SQLite/other: use atomic UPDATE with status check to claim job
            # This avoids race condition by checking status in WHERE clause
            with transaction.atomic():
                job = queryset.first()
                if job:
                    # Atomic claim: only update if still PENDING
                    updated = cls.objects.filter(
                        pk=job.pk,
                        status=cls.Status.PENDING
                    ).update(
                        status=cls.Status.CLAIMED,
                        worker_id=worker_id,
                    )
                    if updated:
                        job.refresh_from_db()
                        return job
                return None

    @classmethod
    def recover_stale_jobs(cls, stale_threshold_minutes=10):
        """
        Recover jobs stuck in CLAIMED/RUNNING state.

        Should be run periodically (e.g., via cron or scheduler).
        """
        from django.utils import timezone
        from datetime import timedelta

        stale_since = timezone.now() - timedelta(minutes=stale_threshold_minutes)
        stale_jobs = cls.objects.filter(
            status__in=[cls.Status.CLAIMED, cls.Status.RUNNING],
            updated_at__lt=stale_since,
        )

        recovered = 0
        for job in stale_jobs:
            if job.can_retry():
                job.status = cls.Status.PENDING
                job.worker_id = ''
                job.retry_count += 1
                job.error = f'Recovered from stale state (worker: {job.worker_id})'
                job.save(update_fields=['status', 'worker_id', 'retry_count', 'error'])
                recovered += 1
            else:
                job.status = cls.Status.DEAD
                job.error = f'Max retries exceeded after stale recovery'
                job.completed_at = timezone.now()
                job.save(update_fields=['status', 'error', 'completed_at'])

        return recovered