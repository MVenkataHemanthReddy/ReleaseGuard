"""
API views for ML models and predictions.
"""

import logging
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.ml.models import MLModel, ModelPrediction, TrainingDataset, FeatureStore
from apps.ml.serializers import (
    MLModelSerializer,
    MLModelCreateSerializer,
    ModelPredictionSerializer,
    ModelPredictionFeedbackSerializer,
    TrainingDatasetSerializer,
    TrainingDatasetCreateSerializer,
    FeatureStoreSerializer,
    MLModelActivateSerializer,
    MLRetrainSerializer,
)
from apps.ml.services import MLModelManager
from apps.projects.models import Project
from apps.core.permissions import IsProjectMember, IsProjectAdmin
from apps.core.exceptions import custom_exception_handler

logger = logging.getLogger(__name__)


class ProjectScopedViewSetMixin:
    """Mixin to scope all queries to user's projects via organisation membership."""

    def get_project(self):
        """Get project from URL kwargs, with permission check."""
        project_id = self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        if not project_id:
            return None

        project = get_object_or_404(Project, pk=project_id)

        # Check membership
        user = self.request.user
        if not user.is_superuser:
            has_access = user.memberships.filter(
                organisation=project.organisation,
                is_active=True,
                organisation__is_active=True,
            ).exists()
            if not has_access:
                self.permission_denied(self.request, message='Not a member of this project\'s organisation')

        return project


class MLModelViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for ML Model management.

    Endpoints:
    - GET    /api/v1/projects/{project_pk}/ml/models/              -> List models
    - POST   /api/v1/projects/{project_pk}/ml/models/              -> Create model record
    - GET    /api/v1/projects/{project_pk}/ml/models/{pk}/         -> Model detail
    - PATCH  /api/v1/projects/{project_pk}/ml/models/{pk}/         -> Update model
    - DELETE /api/v1/projects/{project_pk}/ml/models/{pk}/         -> Soft delete model
    - POST   /api/v1/projects/{project_pk}/ml/models/{pk}/activate/ -> Activate model
    - POST   /api/v1/projects/{project_pk}/ml/models/retrain/      -> Retrain models
    """

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return MLModel.objects.none()
        return MLModel.objects.filter(project=project).select_related('project')

    def get_serializer_class(self):
        if self.action == 'create':
            return MLModelCreateSerializer
        if self.action == 'activate':
            return MLModelActivateSerializer
        if self.action == 'retrain':
            return MLRetrainSerializer
        return MLModelSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def activate(self, request, *args, **kwargs):
        """Activate this model version (deactivates others of same type)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = self.get_object()
        model.activate()

        return Response(MLModelSerializer(model, context=self.get_serializer_context()).data)

    @action(detail=False, methods=['post'], permission_classes=[IsProjectAdmin])
    def retrain(self, request, *args, **kwargs):
        """Trigger retraining of models."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = self.get_project()
        model_types = serializer.validated_data.get('model_types')
        force = serializer.validated_data.get('force', False)

        manager = MLModelManager(project)
        results = manager.retrain_all()

        # Filter by requested model types
        if model_types:
            results = {k: v for k, v in results.items() if k in model_types}

        return Response({
            'message': 'Retraining initiated',
            'results': results,
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def active(self, request, *args, **kwargs):
        """Get all active models for project."""
        project = self.get_project()
        manager = MLModelManager(project)
        active = manager.get_active_models()

        serializer = self.get_serializer(active.values(), many=True)
        return Response(serializer.data)


class ModelPredictionViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Model Prediction queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/ml/predictions/ -> List predictions
    - GET /api/v1/projects/{project_pk}/ml/predictions/{pk}/ -> Prediction detail
    - POST /api/v1/projects/{project_pk}/ml/predictions/{pk}/feedback/ -> Submit feedback
    """

    serializer_class = ModelPredictionSerializer
    permission_classes = [IsProjectMember]
    filterset_fields = ['model', 'target_type', 'status']
    ordering_fields = ['created_at', 'completed_at', 'confidence']
    ordering = ['-created_at']

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return ModelPrediction.objects.none()
        return ModelPrediction.objects.filter(
            model__project=project
        ).select_related('model', 'feedback_by')

    @action(detail=True, methods=['post'], permission_classes=[IsProjectAdmin])
    def feedback(self, request, *args, **kwargs):
        """Submit human feedback on a prediction."""
        prediction = self.get_object()

        serializer = ModelPredictionFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prediction.human_label = serializer.validated_data['human_label']
        prediction.feedback_by = request.user
        prediction.feedback_at = timezone.now()
        prediction.save(update_fields=['human_label', 'feedback_by', 'feedback_at', 'updated_at'])

        return Response(ModelPredictionSerializer(prediction, context=self.get_serializer_context()).data)


class TrainingDatasetViewSet(ProjectScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Training Dataset management.

    Endpoints:
    - GET    /api/v1/projects/{project_pk}/ml/datasets/              -> List datasets
    - POST   /api/v1/projects/{project_pk}/ml/datasets/              -> Create dataset
    - GET    /api/v1/projects/{project_pk}/ml/datasets/{pk}/         -> Dataset detail
    - PATCH  /api/v1/projects/{project_pk}/ml/datasets/{pk}/         -> Update dataset
    - DELETE /api/v1/projects/{project_pk}/ml/datasets/{pk}/         -> Soft delete dataset
    """

    permission_classes = [IsProjectMember]
    lookup_field = 'pk'

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return TrainingDataset.objects.none()
        return TrainingDataset.objects.filter(project=project).select_related('project')

    def get_serializer_class(self):
        if self.action == 'create':
            return TrainingDatasetCreateSerializer
        return TrainingDatasetSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project)


class FeatureStoreViewSet(ProjectScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for Feature Store queries.

    Endpoints:
    - GET /api/v1/projects/{project_pk}/ml/features/ -> List feature vectors
    - GET /api/v1/projects/{project_pk}/ml/features/{pk}/ -> Feature vector detail
    """

    serializer_class = FeatureStoreSerializer
    permission_classes = [IsProjectMember]
    filterset_fields = ['entity_type', 'feature_version']
    ordering_fields = ['computed_at', 'entity_type', 'entity_id']
    ordering = ['-computed_at']

    def get_queryset(self):
        project = self.get_project()
        if not project:
            return FeatureStore.objects.none()
        return FeatureStore.objects.filter(project=project).select_related('project')


# Import timezone
from django.utils import timezone