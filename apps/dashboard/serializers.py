"""
Serializers for Dashboard API.
"""

from rest_framework import serializers
from apps.dashboard.models import (
    DashboardView,
    WidgetConfig,
    UserDashboardPreference,
    DashboardSnapshot,
)
from apps.projects.models import Project
from apps.accounts.models import User


class DashboardViewSerializer(serializers.ModelSerializer):
    """Serializer for DashboardView."""

    user_email = serializers.CharField(source='user.email', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    widget_count = serializers.SerializerMethodField()

    class Meta:
        model = DashboardView
        fields = [
            'id', 'project', 'project_name', 'user', 'user_email',
            'name', 'type', 'description', 'layout', 'widgets',
            'is_default', 'is_shared', 'widget_count',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'user', 'project', 'created_at', 'updated_at', 'deleted_at']

    def get_widget_count(self, obj):
        return len(obj.widgets) if obj.widgets else 0


class DashboardViewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DashboardViews."""

    class Meta:
        model = DashboardView
        fields = ['name', 'type', 'description', 'layout', 'widgets', 'is_default', 'is_shared']

    def validate_layout(self, value):
        """Validate layout structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Layout must be a dictionary')
        return value

    def validate_widgets(self, value):
        """Validate widgets structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Widgets must be a list')
        for widget in value:
            if not isinstance(widget, dict):
                raise serializers.ValidationError('Each widget must be a dictionary')
            if 'widget_type' not in widget:
                raise serializers.ValidationError('Each widget must have widget_type')
        return value


class WidgetConfigSerializer(serializers.ModelSerializer):
    """Serializer for WidgetConfig."""

    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = WidgetConfig
        fields = [
            'id', 'project', 'project_name', 'name', 'widget_type',
            'description', 'config', 'default_size', 'is_enabled',
            'required_permissions', 'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'project', 'created_at', 'updated_at', 'deleted_at']


class WidgetConfigCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating WidgetConfigs."""

    class Meta:
        model = WidgetConfig
        fields = ['name', 'widget_type', 'description', 'config', 'default_size', 'is_enabled', 'required_permissions']


class UserDashboardPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserDashboardPreference."""

    user_email = serializers.CharField(source='user.email', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    default_view_name = serializers.CharField(source='default_view.name', read_only=True)

    class Meta:
        model = UserDashboardPreference
        fields = [
            'id', 'user', 'user_email', 'project', 'project_name',
            'default_view', 'default_view_name', 'theme',
            'auto_refresh', 'refresh_interval_seconds',
            'compact_mode', 'show_timestamps', 'timezone',
            'notify_on_regression', 'notify_on_new_failure', 'notify_on_health_degraded',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'project', 'created_at', 'updated_at']


class UserDashboardPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating UserDashboardPreference."""

    class Meta:
        model = UserDashboardPreference
        fields = [
            'default_view', 'theme', 'auto_refresh', 'refresh_interval_seconds',
            'compact_mode', 'show_timestamps', 'timezone',
            'notify_on_regression', 'notify_on_new_failure', 'notify_on_health_degraded',
        ]


class DashboardSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for DashboardSnapshot."""

    project_name = serializers.CharField(source='project.name', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = DashboardSnapshot
        fields = [
            'id', 'project', 'project_name', 'view_type', 'context',
            'data', 'expires_at', 'is_expired', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.expires_at < timezone.now()


class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data responses."""

    project = serializers.DictField()
    view_type = serializers.CharField()
    context = serializers.DictField()
    widgets = serializers.ListField(child=serializers.DictField())
    metadata = serializers.DictField()
    cached = serializers.BooleanField()
    generated_at = serializers.DateTimeField()


class ProjectDashboardSummarySerializer(serializers.Serializer):
    """Lightweight project dashboard summary for listing."""

    project_id = serializers.UUIDField()
    project_name = serializers.CharField()
    project_slug = serializers.CharField()
    health_status = serializers.CharField()  # green, yellow, red
    recent_release = serializers.DictField(allow_null=True)
    key_metrics = serializers.DictField()
    active_issues_count = serializers.IntegerField()
    failing_api_checks = serializers.IntegerField()
    last_updated = serializers.DateTimeField()