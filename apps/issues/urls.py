"""
URL configuration for issues app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.issues.views import IssueGroupViewSet, ErrorEventViewSet

# Router for standard ViewSets
router = DefaultRouter()
router.register(r'error-events', ErrorEventViewSet, basename='error-event')

# Project-scoped issue routes
project_issues_patterns = [
    path('issues/', IssueGroupViewSet.as_view({'get': 'list', 'post': 'create'}), name='issuegroup-list'),
    path('issues/<uuid:pk>/', IssueGroupViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='issuegroup-detail'),
    path('issues/<uuid:pk>/events/', IssueGroupViewSet.as_view({'get': 'events'}), name='issuegroup-events'),
    path('issues/<uuid:pk>/resolve/', IssueGroupViewSet.as_view({'post': 'resolve'}), name='issuegroup-resolve'),
    path('issues/<uuid:pk>/reopen/', IssueGroupViewSet.as_view({'post': 'reopen'}), name='issuegroup-reopen'),
    path('issues/<uuid:pk>/regression/', IssueGroupViewSet.as_view({'post': 'mark_regression'}), name='issuegroup-regression'),
    path('issues/<uuid:pk>/assign/', IssueGroupViewSet.as_view({'post': 'assign'}), name='issuegroup-assign'),
]

project_issues_patterns += [
    path('', include(router.urls)),
]

urlpatterns = project_issues_patterns