"""
URL configuration for ReleaseGuard project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """API root endpoint with links to all resources."""
    endpoints = {
        'releases': 'Project-scoped: /api/v1/projects/{project_id}/releases/',
        'test-runs': 'Project-scoped: /api/v1/projects/{project_id}/test-runs/',
        'test-cases': 'Project-scoped: /api/v1/projects/{project_id}/test-cases/',
        'analyses': 'Project-scoped: /api/v1/projects/{project_id}/analyses/',
        'api-checks': 'Project-scoped: /api/v1/projects/{project_id}/api-checks/',
        'issues': 'Project-scoped: /api/v1/projects/{project_id}/issues/',
        'ml-models': 'Project-scoped: /api/v1/projects/{project_id}/ml/models/',
        'ml-predictions': 'Project-scoped: /api/v1/projects/{project_id}/ml/predictions/',
        'dashboard': 'Project-scoped: /api/v1/projects/{project_id}/dashboard/overview/',
    }

    # Try to add organisations and projects if they exist
    try:
        endpoints['organisations'] = reverse('organisation-list', request=request, format=format)
    except:
        pass
    try:
        endpoints['projects'] = reverse('project-list', request=request, format=format)
    except:
        pass

    return Response({
        'message': 'Welcome to ReleaseGuard API v1',
        'version': '1.0',
        'documentation': request.build_absolute_uri('/api/docs/'),
        'endpoints': endpoints,
        'authentication': {
            'user': 'Session auth (Django admin)',
            'ci': 'Project token: Authorization: Token <token>',
        },
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for load balancers."""
    from django.db import connection
    try:
        connection.ensure_connection()
        db_status = 'healthy'
    except Exception:
        db_status = 'unhealthy'

    return Response({
        'status': 'ok' if db_status == 'healthy' else 'degraded',
        'database': db_status,
        'version': '1.0',
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API root & health
    path('api/v1/', api_root, name='api-root'),
    path('api/v1/health/', health_check, name='health-check'),

    # API v1 - Project-scoped endpoints
    path('api/v1/projects/<uuid:project_pk>/', include('apps.releases.urls')),
    path('api/v1/projects/<uuid:project_pk>/', include('apps.api_checks.urls')),
    path('api/v1/projects/<uuid:project_pk>/', include('apps.issues.urls')),
    path('api/v1/projects/<uuid:project_pk>/', include('apps.ml.urls')),
    path('api/v1/projects/<uuid:project_pk>/', include('apps.dashboard.urls')),
    path('api/v1/projects/<uuid:project_pk>/', include('apps.projects.urls')),  # environments & project detail

    # Organisations and Projects (list/create)
    path('api/v1/organisations/', include('apps.organizations.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),

    # DRF browsable API login (for session auth)
    path('api-auth/', include('rest_framework.urls')),
]