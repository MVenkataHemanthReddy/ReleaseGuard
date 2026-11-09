"""
ML Models for ReleaseGuard.

Stores model versions, predictions, and training metadata.
All ML is advisory - deterministic rules decide GREEN/YELLOW/RED.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import UUIDTimeStampedSoftDeleteModel, UUIDTimeStampedModel
from apps.projects.models import Project


class MLModel(UUIDTimeStampedSoftDeleteModel):
    """
    Registered ML model version.

    Tracks model type, version, training window, and feature schema.
    """

    class Type(models.TextChoices):
        ANOMALY_DETECTION = 'anomaly_detection', _('Anomaly Detection (Isolation Forest)')
        ERROR_CLUSTERING = 'error_clustering', _('Error Clustering (TF-IDF + KMeans/DBSCAN)')
        FAILURE_CLASSIFICATION = 'failure_classification', _('Failure Classification (Logistic Regression)')

    class Status(models.TextChoices):
        TRAINING = 'training', _('Training')
        ACTIVE = 'active', _('Active')
        DEPRECATED = 'deprecated', _('Deprecated')
        FAILED = 'failed', _('Failed')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ml_models',
        verbose_name=_('project'),
        null=True,
        blank=True,
        help_text=_('Null for global models'),
    )
    name = models.CharField(_('name'), max_length=255)
    type = models.CharField(_('type'), max_length=30, choices=Type.choices, db_index=True)
    version = models.CharField(_('version'), max_length=50, help_text=_('Semantic version, e.g., 1.0.0'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.TRAINING, db_index=True)

    # Model configuration
    algorithm = models.CharField(_('algorithm'), max_length=100, help_text=_('e.g., IsolationForest, KMeans, LogisticRegression'))
    hyperparameters = models.JSONField(_('hyperparameters'), default=dict, blank=True)
    feature_names = models.JSONField(_('feature names'), default=list, help_text=_('Ordered list of feature names'))
    feature_version = models.CharField(_('feature version'), max_length=50, default='1.0')

    # Training metadata
    training_window_start = models.DateTimeField(_('training window start'), null=True, blank=True)
    training_window_end = models.DateTimeField(_('training window end'), null=True, blank=True)
    training_samples = models.PositiveIntegerField(_('training samples'), default=0)
    training_duration_seconds = models.FloatField(_('training duration (s)'), default=0.0)

    # Evaluation metrics (stored as JSON for flexibility)
    evaluation_metrics = models.JSONField(_('evaluation metrics'), default=dict, blank=True)

    # Model artifact storage (path or reference)
    artifact_path = models.CharField(_('artifact path'), max_length=500, blank=True)
    artifact_size_bytes = models.PositiveIntegerField(_('artifact size (bytes)'), default=0)

    # Activation
    activated_at = models.DateTimeField(_('activated at'), null=True, blank=True)
    deprecated_at = models.DateTimeField(_('deprecated at'), null=True, blank=True)

    class Meta:
        verbose_name = _('ML model')
        verbose_name_plural = _('ML models')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name', 'version'],
                name='unique_ml_model_version',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'type', 'status']),
            models.Index(fields=['type', 'status', 'activated_at']),
        ]

    def __str__(self):
        scope = self.project.name if self.project else 'Global'
        return f'{scope} / {self.name} v{self.version} ({self.get_type_display()})'

    def activate(self):
        """Activate this model version, deactivate others of same type/project."""
        from django.db import transaction
        with transaction.atomic():
            # Deactivate other active models of same type for this project
            MLModel.objects.filter(
                project=self.project,
                type=self.type,
                status=MLModel.Status.ACTIVE,
            ).exclude(pk=self.pk).update(
                status=MLModel.Status.DEPRECATED,
                deprecated_at=timezone.now(),
            )
            self.status = MLModel.Status.ACTIVE
            self.activated_at = timezone.now()
            self.save(update_fields=['status', 'activated_at', 'updated_at'])

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class ModelPrediction(UUIDTimeStampedModel):
    """
    Individual ML prediction for a release or error event.

    Advisory only - does not determine release status.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    model = models.ForeignKey(
        MLModel,
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name=_('model'),
    )

    # Target entity (release or error event)
    target_type = models.CharField(_('target type'), max_length=30, choices=[
        ('release', _('Release')),
        ('error_event', _('Error Event')),
        ('api_check', _('API Check')),
    ], db_index=True)
    target_id = models.UUIDField(_('target ID'), db_index=True)

    # Prediction details
    prediction = models.JSONField(_('prediction'), help_text=_('Model output: anomaly_score, cluster_id, class_probs, etc.'))
    confidence = models.FloatField(_('confidence'), null=True, blank=True, help_text=_('Model confidence 0-1 if applicable'))

    # Human feedback (for supervised learning)
    human_label = models.JSONField(_('human label'), null=True, blank=True, help_text=_('Human-provided ground truth'))
    feedback_at = models.DateTimeField(_('feedback at'), null=True, blank=True)
    feedback_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ml_feedback',
        verbose_name=_('feedback by'),
    )

    # Status
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    error_message = models.TextField(_('error message'), blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    class Meta:
        verbose_name = _('model prediction')
        verbose_name_plural = _('model predictions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model', 'target_type', 'target_id']),
            models.Index(fields=['target_type', 'target_id', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.model.name} → {self.target_type}:{self.target_id} = {self.prediction}'


class TrainingDataset(UUIDTimeStampedSoftDeleteModel):
    """
    Curated training dataset for supervised models.

    Built from human-labeled examples (releases, error events).
    """

    class Status(models.TextChoices):
        BUILDING = 'building', _('Building')
        READY = 'ready', _('Ready')
        ARCHIVED = 'archived', _('Archived')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='training_datasets',
        verbose_name=_('project'),
    )
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.BUILDING)

    # Dataset configuration
    target_type = models.CharField(_('target type'), max_length=30, choices=[
        ('release_status', _('Release Status (GREEN/YELLOW/RED)')),
        ('failure_category', _('Failure Category')),
        ('error_cluster', _('Error Cluster')),
    ])
    feature_version = models.CharField(_('feature version'), max_length=50)

    # Data splits
    train_samples = models.PositiveIntegerField(_('train samples'), default=0)
    val_samples = models.PositiveIntegerField(_('validation samples'), default=0)
    test_samples = models.PositiveIntegerField(_('test samples'), default=0)

    # Label distribution
    label_distribution = models.JSONField(_('label distribution'), default=dict, blank=True)

    # Artifact
    artifact_path = models.CharField(_('artifact path'), max_length=500, blank=True)
    ready_at = models.DateTimeField(_('ready at'), null=True, blank=True)

    class Meta:
        verbose_name = _('training dataset')
        verbose_name_plural = _('training datasets')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'name'],
                name='unique_training_dataset_per_project',
            ),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.name} ({self.get_status_display()})'


class FeatureStore(UUIDTimeStampedModel):
    """
    Computed features for ML models.

    Pre-computed feature vectors for releases, error events, etc.
    Enables consistent features across training and inference.
    """

    ENTITY_TYPES = [
        ('release', _('Release')),
        ('error_event', _('Error Event')),
        ('api_check', _('API Check')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='feature_vectors',
        verbose_name=_('project'),
    )
    entity_type = models.CharField(_('entity type'), max_length=30, choices=ENTITY_TYPES, db_index=True)
    entity_id = models.UUIDField(_('entity ID'), db_index=True)

    feature_version = models.CharField(_('feature version'), max_length=50)
    features = models.JSONField(_('features'), help_text=_('Feature name -> value mapping'))
    computed_at = models.DateTimeField(_('computed at'), default=timezone.now)

    class Meta:
        verbose_name = _('feature vector')
        verbose_name_plural = _('feature vectors')
        ordering = ['-computed_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'entity_type', 'entity_id', 'feature_version'],
                name='unique_feature_vector',
            ),
        ]
        indexes = [
            models.Index(fields=['project', 'entity_type', 'feature_version']),
            models.Index(fields=['entity_type', 'entity_id', 'feature_version']),
        ]

    def __str__(self):
        return f'{self.project.name} / {self.entity_type}:{self.entity_id} v{self.feature_version}'