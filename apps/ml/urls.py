"""
URL configuration for ml app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.ml.views import (
    MLModelViewSet,
    ModelPredictionViewSet,
    TrainingDatasetViewSet,
    FeatureStoreViewSet,
)

# Router for standard ViewSets
router = DefaultRouter()
router.register(r'ml/models', MLModelViewSet, basename='mlmodel')
router.register(r'ml/predictions', ModelPredictionViewSet, basename='modelprediction')
router.register(r'ml/datasets', TrainingDatasetViewSet, basename='trainingdataset')
router.register(r'ml/features', FeatureStoreViewSet, basename='featurestore')

urlpatterns = [
    path('', include(router.urls)),
]