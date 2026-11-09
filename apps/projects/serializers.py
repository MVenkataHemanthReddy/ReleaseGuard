from rest_framework import serializers
from .models import Project, Environment, ProjectToken


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ['id', 'name', 'type', 'description', 'base_url', 'is_active', 'is_default']
        read_only_fields = ['id']


class ProjectTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectToken
        fields = ['id', 'name', 'token_prefix', 'description', 'is_active', 'expires_at', 'last_used_at']
        read_only_fields = ['id', 'token_prefix', 'last_used_at']


class ProjectSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source='organisation.name', read_only=True)
    organisation_slug = serializers.CharField(source='organisation.slug', read_only=True)
    environments = EnvironmentSerializer(many=True, read_only=True)
    tokens = ProjectTokenSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'description', 'repository_url', 'is_active',
            'organisation', 'organisation_name', 'organisation_slug',
            'environments', 'tokens',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'organisation_name', 'organisation_slug']