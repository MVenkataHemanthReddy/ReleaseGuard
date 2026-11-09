"""
URL configuration for api_checks app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api_checks.views import ApiCheckViewSet, ApiCheckResultViewSet

# Router for standard ViewSets
router = DefaultRouter()
router.register(r'api-check-results', ApiCheckResultViewSet, basename='api-check-result')

# Project-scoped API check routes
project_api_checks_patterns = [
    path('api-checks/', ApiCheckViewSet.as_view({'get': 'list', 'post': 'create'}), name='apicheck-list'),
    path('api-checks/<uuid:pk>/', ApiCheckViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='apicheck-detail'),
    path('api-checks/<uuid:pk>/run/', ApiCheckViewSet.as_view({'post': 'run'}), name='apicheck-run'),
]

project_api_checks_patterns += [
    path('', include(router.urls)),
]

urlpatterns = project_api_checks_patterns