"""
ShopAPI Demo Views

Contains deliberate regressions for ReleaseGuard testing:

1. Incorrect calculation (pricing bug) - calculate_order_total
2. Broken endpoint (missing import) - broken_endpoint
3. Slow query (N+1 problem) - slow_product_list
4. Unavailable dependency (external service mock) - external_payment_service
5. Intermittent response (random failures) - flaky_checkout
6. Resource-heavy operation (memory leak simulation) - heavy_report
"""

import json
import random
import time
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Prefetch, Sum, F
from django.conf import settings

from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment


# =============================================================================
# REGRESSION 1: Incorrect Calculation (Pricing Bug)
# =============================================================================

def calculate_order_total(request):
    """
    BUG: Incorrect tax calculation - applies tax on discounted amount instead of subtotal.
    Should calculate tax on (subtotal - discount) but currently calculates on subtotal.
    """
    try:
        data = json.loads(request.body) if request.body else {}
        subtotal = Decimal(str(data.get('subtotal', 0)))
        tax_rate = Decimal(str(data.get('tax_rate', 0.1)))  # 10%
        discount = Decimal(str(data.get('discount', 0)))
        shipping = Decimal(str(data.get('shipping', 0)))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # BUG: Tax calculated on full subtotal instead of (subtotal - discount)
    # Correct: tax = (subtotal - discount) * tax_rate
    # Current (buggy): tax = subtotal * tax_rate
    tax = subtotal * tax_rate  # <-- BUG HERE

    total = subtotal - discount + tax + shipping

    return JsonResponse({
        'subtotal': str(subtotal),
        'discount': str(discount),
        'tax': str(tax),
        'shipping': str(shipping),
        'total': str(total),
        'bug_note': 'Tax calculated on full subtotal instead of discounted amount'
    })


# =============================================================================
# REGRESSION 2: Broken Endpoint (Missing Import)
# =============================================================================

@csrf_exempt
def broken_endpoint(request):
    """
    BUG: References undefined variable 'external_service' causing NameError.
    Missing import or initialization of external service client.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
        amount = Decimal(str(data.get('amount', 0)))
        currency = data.get('currency', 'USD')
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # BUG: 'external_service' is not defined - missing import
    # Should be: from .services import external_payment_service
    # external_service = ExternalPaymentService()
    
    # This will raise NameError: name 'external_service' is not defined
    try:
        result = external_service.process_payment(amount, currency)  # <-- BUG HERE
        return JsonResponse({'status': 'success', 'transaction_id': result.get('id')})
    except NameError as e:
        return JsonResponse({
            'error': 'Service unavailable',
            'detail': 'Payment service not configured',
            'regression': 'broken_endpoint_missing_import'
        }, status=503)


# =============================================================================
# REGRESSION 3: Slow Query (N+1 Problem)
# =============================================================================

def slow_product_list(request):
    """
    BUG: N+1 query problem - fetches category for each product individually.
    Should use select_related('category') to fetch in single query.
    """
    # BUG: No select_related - causes N+1 queries
    products = Product.objects.filter(is_active=True)  # <-- BUG: Missing select_related('category')
    
    # This will cause N+1 queries when accessing product.category in loop
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'category': product.category.name,  # <-- Each access triggers separate query
            'category_slug': product.category.slug,
        })
    
    return JsonResponse({
        'products': product_data,
        'count': len(product_data),
        'regression_note': 'N+1 query - missing select_related'
    })


# =============================================================================
# REGRESSION 4: Unavailable Dependency (External Service Mock)
# =============================================================================

def external_payment_service(request):
    """
    BUG: Simulates external payment service being unavailable.
    Randomly returns 503 to simulate dependency failure.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
        amount = Decimal(str(data.get('amount', 0)))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # BUG: Simulate external service being down (10% chance)
    if random.random() < 0.1:
        return JsonResponse({
            'error': 'Payment service temporarily unavailable',
            'code': 'SERVICE_UNAVAILABLE',
            'retry_after': 30,
            'regression': 'external_dependency_failure'
        }, status=503)

    # Simulate successful payment
    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
    
    return JsonResponse({
        'status': 'completed',
        'transaction_id': transaction_id,
        'amount': str(amount),
        'processed_at': timezone.now().isoformat()
    })


# =============================================================================
# REGRESSION 5: Intermittent Response (Random Failures)
# =============================================================================

@csrf_exempt
def flaky_checkout(request):
    """
    BUG: Randomly fails with various error types to simulate flaky behavior.
    ~15% chance of failure with different error types.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
        cart_id = data.get('cart_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # BUG: Random failures simulating flaky behavior
    failure_chance = random.random()
    
    if failure_chance < 0.05:
        # 5% - Timeout simulation
        time.sleep(2)  # Simulate slow response
        return JsonResponse({
            'error': 'Request timeout',
            'code': 'TIMEOUT',
            'regression': 'flaky_timeout'
        }, status=408)
    
    elif failure_chance < 0.10:
        # 5% - Random server error
        return JsonResponse({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'regression': 'flaky_server_error'
        }, status=500)
    
    elif failure_chance < 0.15:
        # 5% - Validation error with wrong field
        return JsonResponse({
            'error': 'Validation failed',
            'field': 'non_existent_field',
            'code': 'VALIDATION_ERROR',
            'regression': 'flaky_validation_error'
        }, status=400)

    # Success case
    return JsonResponse({
        'status': 'completed',
        'order_id': f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}",
        'message': 'Order placed successfully'
    })


# =============================================================================
# REGRESSION 6: Resource-Heavy Operation (Memory Leak Simulation)
# =============================================================================

def heavy_report(request):
    """
    BUG: Creates large in-memory data structures simulating memory leak.
    Generates large CSV-like data in memory without streaming.
    """
    try:
        days = int(request.GET.get('days', 30))
        if days > 365:
            days = 365
    except (TypeError, ValueError):
        days = 30

    # BUG: Builds massive list in memory instead of streaming
    # For 365 days with 1000 orders/day = 365,000 rows in memory
    orders = Order.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=days)
    ).prefetch_related('items__product').order_by('-created_at')

    # BUG: Builds entire report in memory as list of dicts
    report_data = []
    for order in orders:
        for item in order.items.all():
            report_data.append({
                'order_number': order.order_number,
                'order_date': order.created_at.isoformat(),
                'customer': order.user.email if order.user else 'guest',
                'product': item.product_name,
                'quantity': item.quantity,
                'unit_price': str(item.product_price),
                'line_total': str(item.line_total),
                'status': order.status,
            })
    
    # For large datasets, this consumes significant memory
    return JsonResponse({
        'report': report_data,
        'total_rows': len(report_data),
        'generated_at': timezone.now().isoformat(),
        'memory_warning': 'Large dataset loaded entirely in memory',
        'regression': 'memory_heavy_operation'
    })


# =============================================================================
# Correct Implementations (for comparison)
# =============================================================================

def correct_calculate_order_total(request):
    """Correct implementation of order total calculation."""
    try:
        data = json.loads(request.body) if request.body else {}
        subtotal = Decimal(str(data.get('subtotal', 0)))
        tax_rate = Decimal(str(data.get('tax_rate', 0.1)))
        discount = Decimal(str(data.get('discount', 0)))
        shipping = Decimal(str(data.get('shipping', 0)))
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    # CORRECT: Tax on (subtotal - discount)
    taxable_amount = subtotal - discount
    tax = taxable_amount * tax_rate
    total = subtotal - discount + tax + shipping

    return JsonResponse({
        'subtotal': str(subtotal),
        'discount': str(discount),
        'taxable_amount': str(taxable_amount),
        'tax': str(tax),
        'shipping': str(shipping),
        'total': str(total)
    })


def fast_product_list(request):
    """Correct implementation with select_related to avoid N+1."""
    products = Product.objects.filter(is_active=True).select_related('category')
    
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'category': product.category.name,
            'category_slug': product.category.slug,
        })
    
    return JsonResponse({
        'products': product_data,
        'count': len(product_data),
        'optimized': True
    })


def streaming_heavy_report(request):
    """Correct implementation using Django's streaming response."""
    from django.http import StreamingHttpResponse
    import csv
    
    try:
        days = int(request.GET.get('days', 30))
        if days > 365:
            days = 365
    except (TypeError, ValueError):
        days = 30

    orders = Order.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=days)
    ).prefetch_related('items__product').order_by('-created_at')

    def generate():
        # Header
        yield 'order_number,order_date,customer,product,quantity,unit_price,line_total,status\n'
        
        for order in orders.iterator(chunk_size=100):  # Use iterator to avoid loading all
            for item in order.items.all():
                yield f"{order.order_number},{order.created_at.isoformat()},{order.user.email if order.user else 'guest'},{item.product_name},{item.quantity},{item.product_price},{item.line_total},{order.status}\n"
    
    response = StreamingHttpResponse(
        generate(),
        content_type='text/csv'
    )
    response['Content-Disposition'] = f'attachment; filename="orders_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    return response


# =============================================================================
# Class-Based Views (additional regressions)
# =============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ProductListView(View):
    """Product list with optional N+1 bug."""
    
    def get(self, request):
        buggy = request.GET.get('buggy', 'false').lower() == 'true'
        
        if buggy:
            # BUG: N+1
            products = Product.objects.filter(is_active=True)
        else:
            # CORRECT: select_related
            products = Product.objects.filter(is_active=True).select_related('category')
        
        data = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'category': p.category.name if p.category else None,
        } for p in products]
        
        return JsonResponse({'products': data, 'buggy': buggy})


@method_decorator(csrf_exempt, name='dispatch')
class CheckoutView(View):
    """Checkout with flaky behavior."""
    
    def post(self, request):
        # BUG: Random failure
        if random.random() < 0.2:
            return JsonResponse({
                'error': 'Service temporarily unavailable',
                'regression': 'flaky_checkout_class'
            }, status=503)
        
        try:
            data = json.loads(request.body) if request.body else {}
            cart_id = data.get('cart_id')
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'error': 'Invalid input'}, status=400)
        
        # Process order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            subtotal=Decimal('100.00'),
            tax=Decimal('10.00'),
            shipping_cost=Decimal('5.00'),
            total=Decimal('115.00'),
            shipping_name=data.get('shipping_name', 'Test User'),
            shipping_address=data.get('shipping_address', '123 Test St'),
            shipping_phone=data.get('shipping_phone', '555-1234'),
            shipping_email=data.get('shipping_email', 'test@example.com'),
        )
        
        return JsonResponse({
            'status': 'completed',
            'order_id': order.order_number
        })