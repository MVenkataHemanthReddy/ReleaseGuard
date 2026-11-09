"""
Serializers for ReleaseGuard releases API.

Handles ingestion endpoints and dashboard queries.
"""

from rest_framework import serializers
from django.utils import timezone

from apps.releases.models import Release, TestRun, TestCaseResult, ReleaseAnalysis
from apps.projects.models import Project, Environment
from apps.core.permissions import IsProjectMember


class ProjectScopedSerializerMixin:
    """
    Mixin to ensure all operations are scoped to user's projects.
    """

    def get_queryset(self):
        user = self.context['request'].user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(
            project__organisation__memberships__user=user,
            project__organisation__memberships__is_active=True,
            project__organisation__is_active=True,
        )


class EnvironmentSerializer(serializers.ModelSerializer):
    """Serializer for Environment (read-only in release context)."""

    class Meta:
        model = Environment
        fields = ['id', 'name', 'type', 'base_url']
        read_only_fields = fields


class ReleaseSerializer(serializers.ModelSerializer):
    """Serializer for Release model."""

    environment = EnvironmentSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_slug = serializers.CharField(source='project.slug', read_only=True)
    previous_release_version = serializers.SerializerMethodField()
    analysis_status = serializers.CharField(source='analysis.status', read_only=True)
    status = serializers.CharField(source='analysis.status', read_only=True, default='deployed')

    class Meta:
        model = Release
        fields = [
            'id', 'project', 'project_name', 'project_slug', 'environment',
            'version', 'commit_sha', 'commit_short_sha', 'branch',
            'workflow_run_id', 'workflow_run_url', 'commit_message',
            'commit_author', 'commit_timestamp', 'deployed_at',
            'previous_release_version', 'analysis_status', 'status',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

    def get_previous_release_version(self, obj):
        prev = obj.previous_release
        return prev.version if prev else None


class ReleaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating releases (ingestion endpoint)."""

    # Accept environment by name or slug, not just ID
    environment = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Environment.objects.all(),
        required=True,
    )

    class Meta:
        model = Release
        fields = [
            'version', 'commit_sha', 'branch', 'workflow_run_id',
            'workflow_run_url', 'commit_message', 'commit_author',
            'commit_timestamp', 'deployed_at', 'environment',
        ]
        extra_kwargs = {
            'version': {'required': True},
            'commit_sha': {'required': True},
            'branch': {'required': True},
            'workflow_run_id': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter environments to current project
        project = self.context.get('project')
        if project:
            self.fields['environment'].queryset = Environment.objects.filter(project=project)

    def validate_commit_sha(self, value):
        """Validate and normalize commit SHA."""
        value = value.strip().lower()
        if len(value) < 7 or len(value) > 64:
            raise serializers.ValidationError('Commit SHA must be 7-64 characters')
        if not all(c in '0123456789abcdef' for c in value):
            raise serializers.ValidationError('Commit SHA must be hexadecimal')
        return value

    def validate_version(self, value):
        """Validate version string."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Version is required')
        if len(value) > 255:
            raise serializers.ValidationError('Version too long (max 255 chars)')
        return value

    def validate_branch(self, value):
        """Validate branch name."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Branch is required')
        if len(value) > 255:
            raise serializers.ValidationError('Branch name too long')
        return value

    def validate_workflow_run_id(self, value):
        """Validate workflow run ID."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Workflow run ID is required')
        if len(value) > 100:
            raise serializers.ValidationError('Workflow run ID too long')
        return value

    def create(self, validated_data):
        """Create or get existing release (idempotent by workflow_run_id)."""
        project = self.context['project']
        workflow_run_id = validated_data['workflow_run_id']

        # Idempotency: check for existing release with same workflow_run_id
        existing = Release.objects.filter(
            project=project,
            workflow_run_id=workflow_run_id,
        ).first()

        if existing:
            # Update fields that might have changed
            for field, value in validated_data.items():
                setattr(existing, field, value)
            existing.save()
            return existing

        # Compute short SHA
        commit_sha = validated_data['commit_sha']
        validated_data['commit_short_sha'] = commit_sha[:12]

        # Ensure environment is properly set
        environment = validated_data.get('environment')
        if not environment:
            # Try to get environment from context or use project's default
            project = self.context['project']
            environment = Environment.objects.filter(project=project, is_default=True).first()
            if not environment:
                environment = Environment.objects.filter(project=project).first()
        
        release = Release.objects.create(project=project, **validated_data)
        return release


class TestRunSerializer(serializers.ModelSerializer):
    """Serializer for TestRun (read-only for dashboard)."""

    release_version = serializers.CharField(source='release.version', read_only=True)
    pass_rate = serializers.FloatField(read_only=True)
    failure_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = TestRun
        fields = [
            'id', 'release', 'release_version', 'name', 'status',
            'total_tests', 'passed_tests', 'failed_tests', 'skipped_tests',
            'error_tests', 'total_duration', 'pass_rate', 'failure_rate',
            'idempotency_key', 'started_at', 'finished_at',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields


class TestRunUploadSerializer(serializers.Serializer):
    """Serializer for JUnit XML upload."""

    test_run_name = serializers.CharField(
        max_length=255,
        default='default',
        help_text='Test suite name (e.g., "unit", "integration", "e2e")'
    )
    junit_xml = serializers.CharField(
        help_text='Raw JUnit XML content',
        style={'base_template': 'textarea.html'},
    )
    idempotency_key = serializers.CharField(
        max_length=255,
        required=False,
        help_text='Optional custom idempotency key (defaults to workflow_run_id + test_run_name)'
    )

    def validate_junit_xml(self, value):
        """Validate XML size and structure."""
        if not value or not value.strip():
            raise serializers.ValidationError('JUnit XML content is required')

        size_mb = len(value.encode('utf-8')) / (1024 * 1024)
        if size_mb > 10:
            raise serializers.ValidationError(f'XML too large: {size_mb:.1f}MB (max 10MB)')

        # Quick validation
        from apps.releases.parsers import validate_junit_xml
        is_valid, error = validate_junit_xml(value)
        if not is_valid:
            raise serializers.ValidationError(f'Invalid JUnit XML: {error}')

        return value


class TestCaseResultSerializer(serializers.ModelSerializer):
    """Serializer for individual test case results."""

    test_identifier = serializers.CharField(read_only=True)
    is_failure = serializers.BooleanField(read_only=True)

    class Meta:
        model = TestCaseResult
        fields = [
            'id', 'test_run', 'classname', 'name', 'test_identifier',
            'status', 'duration', 'message', 'output', 'traceback',
            'fingerprint', 'properties', 'is_failure',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields


class ReleaseAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for ReleaseAnalysis (policy evaluation result)."""

    release_version = serializers.CharField(source='release.version', read_only=True)
    compared_to_version = serializers.CharField(source='compared_to_release.version', read_only=True)
    failed_rules = serializers.SerializerMethodField()
    warning_rules = serializers.SerializerMethodField()

    class Meta:
        model = ReleaseAnalysis
        fields = [
            'id', 'release', 'release_version', 'status', 'policy_version',
            'rule_results', 'failed_rules', 'warning_rules',
            'new_failures', 'persistent_failures', 'fixed_failures',
            'flaky_tests', 'compared_to_release', 'compared_to_version',
            'evaluated_at', 'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields

    def get_failed_rules(self, obj):
        return obj.get_failed_rules()

    def get_warning_rules(self, obj):
        return obj.get_warning_rules()


class ReleaseCompareSerializer(serializers.Serializer):
    """Serializer for release comparison response."""

    current_release = ReleaseSerializer()
    previous_release = ReleaseSerializer(allow_null=True)
    test_comparison = serializers.DictField()
    new_failures = TestCaseResultSerializer(many=True)
    persistent_failures = TestCaseResultSerializer(many=True)
    fixed_failures = TestCaseResultSerializer(many=True)
    unchanged_passing = TestCaseResultSerializer(many=True)
    summary = serializers.DictField()


class ReleaseDashboardSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project dashboard release list."""

    environment_name = serializers.CharField(source='environment.name', read_only=True)
    environment_type = serializers.CharField(source='environment.type', read_only=True)
    analysis_status = serializers.CharField(source='analysis.status', read_only=True)
    total_tests = serializers.SerializerMethodField()
    failed_tests = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()

    class Meta:
        model = Release
        fields = [
            'id', 'version', 'commit_short_sha', 'branch',
            'environment_name', 'environment_type',
            'deployed_at', 'analysis_status',
            'total_tests', 'failed_tests', 'pass_rate',
        ]

    def get_total_tests(self, obj):
        return obj.test_runs.aggregate(total=models.Sum('total_tests'))['total'] or 0

    def get_failed_tests(self, obj):
        return obj.test_runs.aggregate(total=models.Sum('failed_tests'))['total'] or 0

    def get_pass_rate(self, obj):
        total = self.get_total_tests(obj)
        failed = self.get_failed_tests(obj)
        if total == 0:
            return 0.0
        return ((total - failed) / total) * 100


# Add missing import
from django.db import models