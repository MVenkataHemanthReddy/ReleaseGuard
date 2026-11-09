"""
ShopAPI Demo URLs
"""

from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Regression endpoints
    path('regressions/calculate-total/', views.calculate_order_total, name='calculate-total'),
    path('regressions/broken-endpoint/', views.broken_endpoint, name='broken-endpoint'),
    path('regressions/slow-products/', views.slow_product_list, name='slow-products'),
    path('regressions/external-payment/', views.external_payment_service, name='external-payment'),
    path('regressions/flaky-checkout/', views.flaky_checkout, name='flaky-checkout'),
    path('regressions/heavy-report/', views.heavy_report, name='heavy-report'),
    
    # Correct implementations
    path('correct/calculate-total/', views.correct_calculate_order_total, name='correct-calculate-total'),
    path('correct/fast-products/', views.fast_product_list, name='fast-products'),
    path('correct/streaming-report/', views.streaming_heavy_report, name='streaming-report'),
    
    # Class-based views
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]