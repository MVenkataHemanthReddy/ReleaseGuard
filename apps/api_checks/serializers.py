"""
Serializers for API Health Checks.
"""

from rest_framework import serializers
from apps.api_checks.models import ApiCheck, ApiCheckResult
from apps.projects.models import Environment


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ['id', 'name', 'type']
        read_only_fields = fields


class ApiCheckSerializer(serializers.ModelSerializer):
    """Serializer for ApiCheck configuration."""

    environment = EnvironmentSerializer(read_only=True)
    environment_id = serializers.PrimaryKeyRelatedField(
        queryset=Environment.objects.all(),
        source='environment',
        write_only=True,
        required=False,
        allow_null=True,
    )
    project_name = serializers.CharField(source='project.name', read_only=True)
    recent_results = serializers.SerializerMethodField()
    success_rate_24h = serializers.SerializerMethodField()
    avg_latency_24h = serializers.SerializerMethodField()

    class Meta:
        model = ApiCheck
        fields = [
            'id', 'project', 'project_name', 'environment', 'environment_id',
            'name', 'description',
            'url', 'method', 'expected_status', 'timeout_seconds',
            'headers', 'body', 'expected_content', 'check_ssl',
            'interval_seconds', 'is_active', 'is_critical',
            'recent_results', 'success_rate_24h', 'avg_latency_24h',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'project', 'created_at', 'updated_at', 'deleted_at']

    def get_recent_results(self, obj):
        """Get last 10 results."""
        results = obj.results.order_by('-created_at')[:10]
        return ApiCheckResultSerializer(results, many=True).data

    def get_success_rate_24h(self, obj):
        """Calculate success rate in last 24 hours."""
        from django.utils import timezone
        from datetime import timedelta

        since = timezone.now() - timedelta(hours=24)
        results = obj.results.filter(created_at__gte=since)
        total = results.count()
        if total == 0:
            return None
        success = results.filter(status=ApiCheckResult.Status.SUCCESS).count()
        return round((success / total) * 100, 1)

    def get_avg_latency_24h(self, obj):
        """Average latency in last 24 hours."""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg

        since = timezone.now() - timedelta(hours=24)
        avg = obj.results.filter(
            created_at__gte=since,
            status=ApiCheckResult.Status.SUCCESS,
        ).aggregate(avg=Avg('latency_ms'))['avg']
        return round(avg) if avg else None


class ApiCheckCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API checks."""

    environment = serializers.PrimaryKeyRelatedField(
        queryset=Environment.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ApiCheck
        fields = [
            'name', 'description',
            'url', 'method', 'expected_status', 'timeout_seconds',
            'headers', 'body', 'expected_content', 'check_ssl',
            'interval_seconds', 'is_active', 'is_critical',
            'environment',
        ]

    def validate_url(self, value):
        """Validate URL scheme and basic structure."""
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            raise serializers.ValidationError('Only HTTP and HTTPS URLs are allowed')
        if not parsed.netloc:
            raise serializers.ValidationError('Invalid URL: missing hostname')
        return value

    def validate_timeout_seconds(self, value):
        if value < 1 or value > 300:
            raise serializers.ValidationError('Timeout must be between 1 and 300 seconds')
        return value

    def validate_interval_seconds(self, value):
        if value < 10 or value > 86400:
            raise serializers.ValidationError('Interval must be between 10 seconds and 24 hours')
        return value


class ApiCheckResultSerializer(serializers.ModelSerializer):
    """Serializer for API check results."""

    api_check_name = serializers.CharField(source='api_check.name', read_only=True)
    is_success = serializers.BooleanField(read_only=True)
    total_latency_ms = serializers.IntegerField(read_only=True)

    class Meta:
        model = ApiCheckResult
        fields = [
            'id', 'api_check', 'api_check_name', 'status', 'status_code',
            'latency_ms', 'dns_lookup_ms', 'connect_ms', 'tls_handshake_ms',
            'total_latency_ms', 'response_headers', 'response_body',
            'response_size_bytes', 'error_message', 'error_type',
            'content_match', 'ssl_valid', 'triggered_by', 'is_success',
            'created_at',
        ]
        read_only_fields = fields


class ApiCheckRunSerializer(serializers.Serializer):
    """Serializer for manual check execution."""

    triggered_by = serializers.ChoiceField(
        choices=['manual', 'release'],
        default='manual',
    )
    idempotency_key = serializers.CharField(max_length=255, required=False, allow_blank=True)