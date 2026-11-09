"""
URL configuration for dashboard app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.dashboard.views import (
    DashboardDataViewSet,
    DashboardViewViewSet,
    WidgetConfigViewSet,
    UserDashboardPreferenceViewSet,
)

# Router for standard ViewSets
router = DefaultRouter()
router.register(r'dashboard/views', DashboardViewViewSet, basename='dashboardview')
router.register(r'dashboard/widgets', WidgetConfigViewSet, basename='widgetconfig')
router.register(r'dashboard/preferences', UserDashboardPreferenceViewSet, basename='dashboardpreference')

# Dashboard data endpoints (not RESTful, action-based)
dashboard_data_patterns = [
    path('dashboard/overview/', DashboardDataViewSet.as_view({'get': 'overview'}), name='dashboard-overview'),
    path('dashboard/release-detail/', DashboardDataViewSet.as_view({'get': 'release_detail'}), name='dashboard-release-detail'),
    path('dashboard/api-health/', DashboardDataViewSet.as_view({'get': 'api_health'}), name='dashboard-api-health'),
    path('dashboard/test-intelligence/', DashboardDataViewSet.as_view({'get': 'test_intelligence'}), name='dashboard-test-intelligence'),
    path('dashboard/issues/', DashboardDataViewSet.as_view({'get': 'issues'}), name='dashboard-issues'),
    path('dashboard/summary/', DashboardDataViewSet.as_view({'get': 'summary'}), name='dashboard-summary'),
]

urlpatterns = dashboard_data_patterns + [
    path('', include(router.urls)),
]