"""
Serializers for ML API.
"""

from rest_framework import serializers
from apps.ml.models import MLModel, ModelPrediction, TrainingDataset, FeatureStore
from apps.projects.models import Project


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for ML model configurations."""

    project_name = serializers.CharField(source='project.name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    predictions_count = serializers.SerializerMethodField()

    class Meta:
        model = MLModel
        fields = [
            'id', 'project', 'project_name', 'name', 'type', 'version',
            'algorithm', 'hyperparameters', 'feature_names', 'feature_version',
            'status', 'training_window_start', 'training_window_end',
            'training_samples', 'training_duration_seconds',
            'evaluation_metrics', 'artifact_path', 'artifact_size_bytes',
            'activated_at', 'deprecated_at', 'is_active', 'predictions_count',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields

    def get_predictions_count(self, obj):
        return obj.predictions.count()


class MLModelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ML models."""

    class Meta:
        model = MLModel
        fields = [
            'name', 'type', 'version', 'algorithm', 'hyperparameters',
            'feature_names', 'feature_version',
        ]

    def validate_version(self, value):
        """Validate semantic version format."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$', value):
            raise serializers.ValidationError('Version must be semantic (e.g., 1.0.0)')
        return value


class ModelPredictionSerializer(serializers.ModelSerializer):
    """Serializer for model predictions."""

    model_name = serializers.CharField(source='model.name', read_only=True)
    model_type = serializers.CharField(source='model.type', read_only=True)
    model_version = serializers.CharField(source='model.version', read_only=True)
    target_display = serializers.SerializerMethodField()

    class Meta:
        model = ModelPrediction
        fields = [
            'id', 'model', 'model_name', 'model_type', 'model_version',
            'target_type', 'target_id', 'target_display',
            'prediction', 'confidence', 'human_label',
            'feedback_at', 'feedback_by', 'status', 'error_message',
            'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_target_display(self, obj):
        return f'{obj.target_type}:{obj.target_id}'


class ModelPredictionFeedbackSerializer(serializers.Serializer):
    """Serializer for submitting human feedback on predictions."""

    human_label = serializers.JSONField(help_text='Ground truth label')
    feedback_by = serializers.HiddenField(default=serializers.CurrentUserDefault())


class TrainingDatasetSerializer(serializers.ModelSerializer):
    """Serializer for training datasets."""

    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = TrainingDataset
        fields = [
            'id', 'project', 'project_name', 'name', 'description',
            'status', 'target_type', 'feature_version',
            'train_samples', 'val_samples', 'test_samples',
            'label_distribution', 'artifact_path', 'ready_at',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = fields


class TrainingDatasetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating training datasets."""

    class Meta:
        model = TrainingDataset
        fields = ['name', 'description', 'target_type', 'feature_version']


class FeatureStoreSerializer(serializers.ModelSerializer):
    """Serializer for feature vectors."""

    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = FeatureStore
        fields = [
            'id', 'project', 'project_name', 'entity_type', 'entity_id',
            'feature_version', 'features', 'computed_at',
        ]
        read_only_fields = fields


class MLModelActivateSerializer(serializers.Serializer):
    """Serializer for activating an ML model."""

    confirm = serializers.BooleanField(default=False, help_text='Confirm activation (deactivates other models of same type)')

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError('Must confirm activation')
        return value


class MLRetrainSerializer(serializers.Serializer):
    """Serializer for triggering model retraining."""

    model_types = serializers.MultipleChoiceField(
        choices=MLModel.Type.choices,
        required=False,
        help_text='Model types to retrain (default: all)',
    )
    force = serializers.BooleanField(default=False, help_text='Force retrain even if active model exists')