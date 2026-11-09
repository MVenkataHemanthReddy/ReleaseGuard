from django.urls import path
from .views import (
    ProjectListCreateView, 
    ProjectDetailView,
    EnvironmentListCreateView,
    EnvironmentDetailView,
    ProjectTokenCreateView
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    
    # Environment endpoints
    path('environments/', EnvironmentListCreateView.as_view(), name='environment-list-create'),
    path('environments/<uuid:pk>/', EnvironmentDetailView.as_view(), name='environment-detail'),
    
    # Token endpoints
    path('tokens/', ProjectTokenCreateView.as_view(), name='token-create'),
]