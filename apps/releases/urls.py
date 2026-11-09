"""
URL configuration for releases app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.releases.views import (
    ReleaseViewSet,
    TestRunUploadView,
    TestRunViewSet,
    TestCaseResultViewSet,
    ReleaseAnalysisViewSet,
)

# Router for standard ViewSets
router = DefaultRouter()
router.register(r'test-runs', TestRunViewSet, basename='testrun')
router.register(r'test-cases', TestCaseResultViewSet, basename='testcase')
router.register(r'analyses', ReleaseAnalysisViewSet, basename='analysis')

# Project-scoped release routes
project_releases_patterns = [
    path('releases/', ReleaseViewSet.as_view({'get': 'list', 'post': 'create'}), name='release-list'),
    path('releases/dashboard/', ReleaseViewSet.as_view({'get': 'dashboard'}), name='release-dashboard'),
    path('releases/<uuid:pk>/', ReleaseViewSet.as_view({'get': 'retrieve'}), name='release-detail'),
    path('releases/<uuid:pk>/compare/', ReleaseViewSet.as_view({'get': 'compare'}), name='release-compare'),
    path('releases/<uuid:release_pk>/test-runs/', TestRunUploadView.as_view({'get': 'list', 'post': 'create'}), name='testrun-upload'),
]

# Include router URLs under project scope - only for test-runs, test-cases, analyses
project_releases_patterns += router.urls

urlpatterns = project_releases_patterns