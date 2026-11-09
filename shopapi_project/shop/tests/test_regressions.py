"""
Tests for ShopAPI Regressions

These tests verify the deliberate regressions exist and document expected behavior.
Run with: pytest shop/tests/test_regressions.py -v
"""

import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from shop.models import Product, Category, Cart, CartItem, Order, OrderItem


User = get_user_model()


class RegressionTestBase(TestCase):
    """Base class for regression tests."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('99.99'),
            cost_price=Decimal('50.00'),
            category=self.category,
            stock=10,
            is_active=True
        )


class TestIncorrectCalculation(RegressionTestBase):
    """Test the incorrect tax calculation regression."""
    
    def test_incorrect_tax_calculation(self):
        """Test that tax is incorrectly calculated on full subtotal."""
        url = reverse('shop:calculate-total')
        data = {
            'subtotal': '100.00',
            'tax_rate': '0.10',  # 10%
            'discount': '20.00',
            'shipping': '5.00'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # BUG: Tax calculated on 100 instead of (100 - 20) = 80
        # Expected correct tax: 80 * 0.10 = 8.00
        # Buggy tax: 100 * 0.10 = 10.00
        self.assertEqual(float(result['tax']), 10.00)  # Bug: should be 8.00
        self.assertEqual(float(result['total']), 95.00)  # 100 - 20 + 10 + 5 = 95
        # Correct total should be: 100 - 20 + 8 + 5 = 93
        
    def test_correct_calculation(self):
        """Test the correct calculation endpoint."""
        url = reverse('shop:correct-calculate-total')
        data = {
            'subtotal': '100.00',
            'tax_rate': '0.10',
            'discount': '20.00',
            'shipping': '5.00'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Correct: tax on (100 - 20) = 80 * 0.10 = 8.00
        self.assertEqual(float(result['tax']), 8.00)
        # Correct total: 100 - 20 + 8 + 5 = 93
        self.assertEqual(float(result['total']), 93.00)


class TestBrokenEndpoint(RegressionTestBase):
    """Test the broken endpoint regression."""
    
    def test_broken_endpoint_returns_503(self):
        """Test that broken endpoint returns 503 due to missing import."""
        url = reverse('shop:broken-endpoint')
        data = {'amount': '100.00', 'currency': 'USD'}
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 503)
        result = response.json()
        self.assertIn('regression', result)
        self.assertEqual(result['regression'], 'broken_endpoint_missing_import')


class TestSlowQueryNPlusOne(RegressionTestBase):
    """Test the N+1 query regression."""
    
    def test_n_plus_one_query(self):
        """Test that slow endpoint doesn't use select_related."""
        # Create additional products
        for i in range(5):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                category=self.category,
                stock=5,
                is_active=True
            )
        
        url = reverse('shop:slow-products')
        
        # Count queries
        with self.assertNumQueries(7):  # 1 for products + 1 for each category access (6 products)
            response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['count'], 6)
        self.assertIn('regression_note', result)


class TestFastProductList(RegressionTestBase):
    """Test the optimized product list."""
    
    def test_fast_product_list_uses_select_related(self):
        """Test that fast endpoint uses select_related."""
        for i in range(5):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                category=self.category,
                stock=5,
                is_active=True
            )
        
        url = reverse('shop:fast-products')
        
        # Should use select_related - Django optimizes to single query with JOIN
        with self.assertNumQueries(1):
            response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['count'], 6)
        self.assertTrue(result.get('optimized', False))


class TestExternalPaymentService(RegressionTestBase):
    """Test the external payment service regression."""
    
    def test_external_service_unavailable(self):
        """Test that external service returns 503 ~10% of the time."""
        url = reverse('shop:external-payment')
        data = {'amount': '100.00'}
        
        # Run multiple times to catch the 10% failure rate
        responses = []
        for _ in range(100):
            response = self.client.post(
                url,
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Should have some 503s (approximately 10%)
        error_503_count = responses.count(503)
        self.assertGreater(error_503_count, 0)  # At least some failures
        self.assertLess(error_503_count, 20)    # But not too many (10% ± variance)


class TestFlakyCheckout(RegressionTestBase):
    """Test the flaky checkout regression."""
    
    def test_flaky_checkout_failures(self):
        """Test that flaky checkout fails ~15% of the time."""
        url = reverse('shop:flaky-checkout')
        data = {'cart_id': 'test-cart'}
        
        responses = []
        for _ in range(200):
            response = self.client.post(
                url,
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Should have ~15% failures (408, 500, 400)
        failure_codes = [408, 500, 400]
        failure_count = sum(1 for code in responses if code in failure_codes)
        
        # Should have failures but not too many
        self.assertGreater(failure_count, 10)   # At least some failures
        self.assertLess(failure_count, 50)      # But not too many (~15% ± variance)


class TestHeavyReport(RegressionTestBase):
    """Test the heavy report regression."""
    
    def test_heavy_report_returns_data(self):
        """Test that heavy report returns data but warns about memory."""
        url = reverse('shop:heavy-report')
        
        # Create some orders
        for i in range(3):
            order = Order.objects.create(
                user=self.user,
                order_number=f'ORD-20240101-{i:04d}',
                subtotal=Decimal('100.00'),
                tax=Decimal('10.00'),
                shipping_cost=Decimal('5.00'),
                total=Decimal('115.00'),
                shipping_name='Test User',
                shipping_address='123 Test St',
                shipping_phone='555-1234',
                shipping_email='test@example.com'
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                product_name=self.product.name,
                product_price=self.product.price,
                quantity=1,
                line_total=self.product.price
            )
        
        response = self.client.get(reverse('shop:heavy-report'), {'days': '30'})
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn('report', result)
        self.assertGreater(result['total_rows'], 0)
        self.assertIn('memory_warning', result)


class TestStreamingReport(RegressionTestBase):
    """Test the streaming report (correct implementation)."""
    
    def test_streaming_report_returns_csv(self):
        """Test that streaming report returns CSV."""
        url = reverse('shop:streaming-report')
        
        response = self.client.get(url, {'days': '30'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])


class TestProductListView(RegressionTestBase):
    """Test the ProductListView with buggy parameter."""
    
    def test_product_list_buggy_true(self):
        """Test that buggy=true triggers N+1."""
        for i in range(3):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                category=self.category,
                stock=5,
                is_active=True
            )
        
        url = reverse('shop:product-list')
        
        with self.assertNumQueries(5):  # 1 for products + 1 per category access (4 total)
            response = self.client.get(url, {'buggy': 'true'})
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['buggy'])
    
    def test_product_list_buggy_false(self):
        """Test that buggy=false uses select_related."""
        for i in range(3):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                category=self.category,
                stock=5,
                is_active=True
            )
        
        url = reverse('shop:product-list')
        
        with self.assertNumQueries(1):  # Single query with JOIN
            response = self.client.get(url, {'buggy': 'false'})
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertFalse(result['buggy'])


class TestCheckoutView(RegressionTestBase):
    """Test the CheckoutView flaky behavior."""
    
    def test_checkout_flaky(self):
        """Test that checkout has 20% failure rate."""
        url = reverse('shop:checkout')
        data = {
            'cart_id': 'test-cart',
            'shipping_name': 'Test User',
            'shipping_address': '123 Test St',
            'shipping_phone': '555-1234',
            'shipping_email': 'test@example.com'
        }
        
        self.client.force_login(self.user)
        
        responses = []
        for _ in range(100):
            response = self.client.post(
                url,
                data=json.dumps(data),
                content_type='application/json'
            )
            responses.append(response.status_code)
        
        # Should have ~20% failures (503)
        failure_count = responses.count(503)
        self.assertGreater(failure_count, 5)
        self.assertLess(failure_count, 35)


# Run with: pytest shop/tests/test_regressions.py -v