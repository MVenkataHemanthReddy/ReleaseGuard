"""
Serializers for Issues API.
"""

from rest_framework import serializers
from apps.issues.models import IssueGroup, ErrorEvent
from apps.projects.models import Environment
from apps.releases.models import Release
from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']
        read_only_fields = fields


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ['id', 'name', 'type']
        read_only_fields = fields


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ['id', 'version', 'commit_short_sha', 'branch', 'deployed_at']
        read_only_fields = fields


class ErrorEventSerializer(serializers.ModelSerializer):
    """Serializer for individual error events."""

    issue_group_title = serializers.CharField(source='issue_group.title', read_only=True)
    release_version = serializers.CharField(source='release.version', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    timestamp = serializers.DateTimeField(source='occurred_at', read_only=True)

    class Meta:
        model = ErrorEvent
        fields = [
            'id', 'issue_group', 'issue_group_title', 'project', 'release', 'release_version',
            'environment', 'environment_name', 'source', 'source_display', 'source_id',
            'fingerprint', 'exception_class', 'message', 'traceback', 'context',
            'occurred_at', 'timestamp', 'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields


class ErrorEventCreateSerializer(serializers.Serializer):
    """Serializer for manual error event ingestion."""

    fingerprint = serializers.CharField(max_length=64)
    exception_class = serializers.CharField(max_length=255)
    message = serializers.CharField(allow_blank=True, required=False)
    traceback = serializers.CharField(allow_blank=True, required=False)
    context = serializers.JSONField(required=False, default=dict)
    release_id = serializers.UUIDField(required=False, allow_null=True)
    environment_id = serializers.UUIDField(required=False, allow_null=True)


class IssueGroupSerializer(serializers.ModelSerializer):
    """Serializer for issue groups (list view)."""

    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to = UserSerializer(read_only=True)
    first_seen_release_version = serializers.CharField(source='first_seen_release.version', read_only=True)
    last_seen_release_version = serializers.CharField(source='last_seen_release.version', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    first_seen = serializers.DateTimeField(source='first_seen_at', read_only=True)
    last_seen = serializers.DateTimeField(source='last_seen_at', read_only=True)
    occurrences = serializers.IntegerField(source='occurrence_count', read_only=True)
    recent_events = serializers.SerializerMethodField()

    class Meta:
        model = IssueGroup
        fields = [
            'id', 'project', 'project_name', 'fingerprint', 'title', 'description',
            'error_type', 'exception_class', 'status', 'status_display', 'is_regression',
            'first_seen_at', 'last_seen_at', 'occurrence_count',
            'first_seen', 'last_seen', 'occurrences',
            'first_seen_release', 'first_seen_release_version',
            'last_seen_release', 'last_seen_release_version',
            'assigned_to', 'tags', 'recent_events',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields

    def get_recent_events(self, obj):
        """Get last 5 error events."""
        events = obj.error_events.order_by('-occurred_at')[:5]
        return ErrorEventSerializer(events, many=True).data


class IssueGroupDetailSerializer(IssueGroupSerializer):
    """Serializer for issue group detail view with full event list."""

    events = ErrorEventSerializer(source='error_events', many=True, read_only=True)

    class Meta(IssueGroupSerializer.Meta):
        fields = IssueGroupSerializer.Meta.fields + ['events']


class IssueGroupUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating issue group (status, assignment, tags)."""

    status = serializers.ChoiceField(choices=IssueGroup.Status.choices, required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    tags = serializers.JSONField(required=False)
    is_regression = serializers.BooleanField(required=False)

    class Meta:
        model = IssueGroup
        fields = ['status', 'assigned_to', 'tags', 'is_regression', 'description']

    def validate_status(self, value):
        """Validate status transition."""
        instance = self.instance
        if instance:
            valid_transitions = {
                IssueGroup.Status.OPEN: [IssueGroup.Status.IN_PROGRESS, IssueGroup.Status.RESOLVED, IssueGroup.Status.IGNORED],
                IssueGroup.Status.IN_PROGRESS: [IssueGroup.Status.RESOLVED, IssueGroup.Status.OPEN, IssueGroup.Status.IGNORED],
                IssueGroup.Status.RESOLVED: [IssueGroup.Status.OPEN],  # Reopen
                IssueGroup.Status.IGNORED: [IssueGroup.Status.OPEN],
            }
            if instance.status in valid_transitions:
                if value not in valid_transitions[instance.status]:
                    raise serializers.ValidationError(f'Cannot transition from {instance.status} to {value}')
        return value