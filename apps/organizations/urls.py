from django.urls import path
from .views import OrganisationListCreateView, OrganisationDetailView

app_name = 'organizations'

urlpatterns = [
    path('', OrganisationListCreateView.as_view(), name='organisation-list-create'),
    path('<uuid:pk>/', OrganisationDetailView.as_view(), name='organisation-detail'),
]