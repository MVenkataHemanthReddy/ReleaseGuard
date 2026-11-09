"""
Dashboard models for ReleaseGuard.

Stores user dashboard preferences, saved views, and widget configurations.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel, UUIDTimeStampedModel
from apps.projects.models import Project


class DashboardView(UUIDTimeStampedSoftDeleteModel):
    """
    Saved dashboard view configuration.

    Users can create custom dashboard layouts with selected widgets.
    """

    class Type(models.TextChoices):
        PROJECT_OVERVIEW = 'project_overview', _('Project Overview')
        RELEASE_DETAIL = 'release_detail', _('Release Detail')
        API_HEALTH = 'api_health', _('API Health')
        TEST_INTELLIGENCE = 'test_intelligence', _('Test Intelligence')
        ISSUES = 'issues', _('Issues')
        CUSTOM = 'custom', _('Custom')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='dashboard_views',
        verbose_name=_('project'),
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='dashboard_views',
        verbose_name=_('user'),
    )
    name = models.CharField(_('name'), max_length=255)
    type = models.CharField(_('type'), max_length=30, choices=Type.choices, default=Type.CUSTOM)
    description = models.TextField(_('description'), blank=True)

    # Layout configuration (JSON)
    layout = models.JSONField(_('layout'), default=dict, help_text=_('Grid layout configuration'))
    widgets = models.JSONField(_('widgets'), default=list, help_text=_('Widget configurations'))

    # Sharing
    is_default = models.BooleanField(_('default'), default=False)
    is_shared = models.BooleanField(_('shared'), default=False)

    class Meta:
        verbose_name = _('dashboard view')
        verbose_name_plural = _('dashboard views')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user', 'name'],
                name='unique_dashboard_view_per_user',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'user', 'is_default']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.user.email} / {self.name}'


class WidgetConfig(UUIDTimeStampedSoftDeleteModel):
    """
    Reusable widget configuration.

    Defines a widget type and its configuration options.
    """

    class WidgetType(models.TextChoices):
        # Project overview
        HEALTH_SUMMARY = 'health_summary', _('Health Summary')
        RECENT_RELEASES = 'recent_releases', _('Recent Releases')
        KEY_METRICS = 'key_metrics', _('Key Metrics')
        TREND_CHART = 'trend_chart', _('Trend Chart')

        # Release detail
        RELEASE_HEADER = 'release_header', _('Release Header')
        TEST_SUMMARY = 'test_summary', _('Test Summary')
        COMPARISON_CHART = 'comparison_chart', _('Comparison Chart')
        POLICY_EXPLANATION = 'policy_explanation', _('Policy Explanation')
        FAILURE_BREAKDOWN = 'failure_breakdown', _('Failure Breakdown')

        # API health
        API_CHECK_LIST = 'api_check_list', _('API Check List')
        LATENCY_CHART = 'latency_chart', _('Latency Chart')
        UPTIME_CHART = 'uptime_chart', _('Uptime Chart')
        STATUS_TIMELINE = 'status_timeline', _('Status Timeline')

        # Test intelligence
        TEST_TRENDS = 'test_trends', _('Test Trends')
        FLAKY_TESTS = 'flaky_tests', _('Flaky Tests')
        DURATION_TRENDS = 'duration_trends', _('Duration Trends')
        NEW_FAILURES = 'new_failures', _('New Failures')

        # Issues
        ISSUE_LIST = 'issue_list', _('Issue List')
        ISSUE_TREND = 'issue_trend', _('Issue Trend')
        TOP_ERRORS = 'top_errors', _('Top Errors')
        REGRESSION_ALERTS = 'regression_alerts', _('Regression Alerts')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='widget_configs',
        verbose_name=_('project'),
    )
    name = models.CharField(_('name'), max_length=255)
    widget_type = models.CharField(_('widget type'), max_length=30, choices=WidgetType.choices)
    description = models.TextField(_('description'), blank=True)

    # Configuration options
    config = models.JSONField(_('config'), default=dict, help_text=_('Widget-specific configuration'))
    default_size = models.JSONField(_('default size'), default=dict, help_text=_('Default grid size {w, h}'))

    # Availability
    is_enabled = models.BooleanField(_('enabled'), default=True)
    required_permissions = models.JSONField(_('required permissions'), default=list, blank=True)

    class Meta:
        verbose_name = _('widget config')
        verbose_name_plural = _('widget configs')
        ordering = ['widget_type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'widget_type', 'name'],
                name='unique_widget_config_per_project',
            ),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.get_widget_type_display()}'


class UserDashboardPreference(UUIDTimeStampedModel):
    """
    User-specific dashboard preferences.

    Stores per-user settings like default view, theme, refresh intervals.
    """

    class Theme(models.TextChoices):
        LIGHT = 'light', _('Light')
        DARK = 'dark', _('Dark')
        AUTO = 'auto', _('Auto (System)')

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='dashboard_preferences',
        verbose_name=_('user'),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name=_('project'),
    )

    # View preferences
    default_view = models.ForeignKey(
        DashboardView,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for_users',
        verbose_name=_('default view'),
    )
    theme = models.CharField(_('theme'), max_length=10, choices=Theme.choices, default=Theme.AUTO)

    # Refresh settings
    auto_refresh = models.BooleanField(_('auto refresh'), default=True)
    refresh_interval_seconds = models.PositiveIntegerField(_('refresh interval (s)'), default=30)

    # Display preferences
    compact_mode = models.BooleanField(_('compact mode'), default=False)
    show_timestamps = models.BooleanField(_('show timestamps'), default=True)
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')

    # Notification preferences
    notify_on_regression = models.BooleanField(_('notify on regression'), default=True)
    notify_on_new_failure = models.BooleanField(_('notify on new failure'), default=True)
    notify_on_health_degraded = models.BooleanField(_('notify on health degraded'), default=True)

    class Meta:
        verbose_name = _('user dashboard preference')
        verbose_name_plural = _('user dashboard preferences')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'project'],
                name='unique_preference_per_user_project',
            ),
        ]

    def __str__(self):
        return f'{self.user.email} @ {self.project.name}'


class DashboardSnapshot(UUIDTimeStampedModel):
    """
    Cached dashboard data snapshots for performance.

    Stores pre-computed dashboard data that can be served quickly.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='dashboard_snapshots',
        verbose_name=_('project'),
    )
    view_type = models.CharField(_('view type'), max_length=30, choices=[
        ('project_overview', 'Project Overview'),
        ('release_detail', 'Release Detail'),
        ('api_health', 'API Health'),
        ('test_intelligence', 'Test Intelligence'),
        ('issues', 'Issues'),
    ], db_index=True)

    # Context (release_id for release detail, etc.)
    context = models.JSONField(_('context'), default=dict)

    # Snapshot data
    data = models.JSONField(_('data'))
    expires_at = models.DateTimeField(_('expires at'), db_index=True)

    class Meta:
        verbose_name = _('dashboard snapshot')
        verbose_name_plural = _('dashboard snapshots')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'view_type', 'expires_at']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.view_type} / {self.context}'

    @classmethod
    def get_valid_snapshot(cls, project, view_type, context):
        """Get valid snapshot if exists and not expired."""
        from django.utils import timezone
        from django.db import connection

        if connection.vendor == 'sqlite':
            qs = cls.objects.filter(
                project=project,
                view_type=view_type,
                expires_at__gt=timezone.now(),
            )
            for item in qs:
                if isinstance(item.context, dict) and all(item.context.get(k) == v for k, v in context.items()):
                    return item
            return None

        # PostgreSQL support
        return cls.objects.filter(
            project=project,
            view_type=view_type,
            context__contains=context,
            expires_at__gt=timezone.now(),
        ).first()

    @classmethod
    def create_snapshot(cls, project, view_type, context, data, ttl_seconds=300):
        """Create or update snapshot with TTL."""
        from django.utils import timezone
        from datetime import timedelta
        from django.core.serializers.json import DjangoJSONEncoder
        import json

        expires_at = timezone.now() + timedelta(seconds=ttl_seconds)

        # Ensure all datetimes, UUIDs, Decimals are safely serialized to JSON primitives
        serializable_data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))

        snapshot, created = cls.objects.update_or_create(
            project=project,
            view_type=view_type,
            context=context,
            defaults={
                'data': serializable_data,
                'expires_at': expires_at,
            }
        )
        return snapshot