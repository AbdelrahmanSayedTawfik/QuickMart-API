# ═══════════════════════════════════════════════════════════════
# apps/orders/tests/test_orders.py
# ═══════════════════════════════════════════════════════════════

from urllib import response
from apps.conftest import auth_client, order
import pytest
from rest_framework import status
from apps.orders.models import Order, CartItem


@pytest.mark.django_db
class TestCartOperations:
    """
    Tests for cart endpoints.
    """
    
    def test_add_item_to_cart(self, auth_client, product):
        """
        Test: Add product to cart.
        """
        response = auth_client.post('/api/cart/add/', {
            'product': product.id,
            'quantity': 3
        }, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 3
        assert response.data['product'] == product.id
    
    def test_add_unavailable_product_fails(self, auth_client, out_of_stock_product):
        """
        Test: Cannot add out-of-stock product to cart.
        """
        response = auth_client.post('/api/cart/add/', {
            'product': out_of_stock_product.id,
            'quantity': 1
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_remove_item_from_cart(self, auth_client, cart_with_items, product):
        """
        Test: Remove item from cart.
        """
        response = auth_client.delete('/api/cart/remove/', {
            'product': product.id
        }, format='json')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_clear_cart(self, auth_client, cart_with_items):
        """
        Test: Clear all items from cart.
        """
        response = auth_client.delete('/api/cart/clear/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestCheckout:
    """
    Tests for POST /api/orders/checkout/
    """
    
    def test_checkout_empty_cart_fails(self, auth_client):
        """
        Test: Cannot checkout with empty cart.
        """
        response = auth_client.post('/api/orders/checkout/', {
            'delivery_address': '123 Test St',
            'delivery_city': 'Cairo',
            'delivery_phone': '01012345678'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'empty' in str(response.data).lower()
    
    def test_checkout_success(self, auth_client, cart_with_items):
        """
        Test: Successful checkout creates order.
        """
        response = auth_client.post('/api/orders/checkout/', {
            'delivery_address': '123 Test St, Cairo',
            'delivery_city': 'Cairo',
            'delivery_phone': '01012345678',
            'notes': 'Please call before delivery'
        }, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_number' in response.data
        assert response.data['order_number'].startswith('QM-')
        assert response.data['status'] == 'pending'
        assert float(response.data['total']) > 0
        
        # Verify order was created in database
        order = Order.objects.get(order_number=response.data['order_number'])
        assert order.user.username == 'customer1'
        assert order.items.count() == 1
    
    def test_checkout_reduces_stock(self, auth_client, cart_with_items, product):
        """
        Test: Checkout reduces product stock.
        """
        initial_stock = product.stock_quantity
        
        auth_client.post('/api/orders/checkout/', {
            'delivery_address': '123 Test St',
            'delivery_city': 'Cairo',
            'delivery_phone': '01012345678'
        }, format='json')
        
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 2  # 2 items in cart
    
    def test_checkout_clears_cart(self, auth_client, cart_with_items):
        """
        Test: Checkout clears the cart.
        """
        auth_client.post('/api/orders/checkout/', {
            'delivery_address': '123 Test St',
            'delivery_city': 'Cairo',
            'delivery_phone': '01012345678'
        }, format='json')
        
        # Cart should be empty now
        response = auth_client.get('/api/cart/')
        assert len(response.data['items']) == 0


@pytest.mark.django_db
class TestOrderManagement:
    """
    Tests for order listing and cancellation.
    """
    
    def test_list_my_orders(self, auth_client, order):
        response = auth_client.get('/api/orders/')

        assert response.status_code == status.HTTP_200_OK

    
        if 'results' in response.data:
            # Paginated response
            orders_data = response.data['results']
        else:
            # Non-paginated response
            orders_data = response.data

        assert len(orders_data) >= 1
        assert orders_data[0]['order_number'] == order.order_number
    
    def test_cancel_pending_order(self, auth_client, order):
        """
        Test: Can cancel pending order.
        """
        response = auth_client.post(f'/api/orders/{order.order_number}/cancel/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'cancelled' in response.data['message'].lower()
        
        order.refresh_from_db()
        assert order.status == 'cancelled'
    
    def test_cancel_shipped_order_fails(self, auth_client, order):
        """
        Test: Cannot cancel already shipped order.
        """
        order.status = 'shipped'
        order.save()
        
        response = auth_client.post(f'/api/orders/{order.order_number}/cancel/')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_cancel_other_user_order_fails(self, api_client, seller_user, order):
        """
        Test: Cannot cancel another user's order.
        """
        api_client.force_authenticate(user=seller_user)
        
        response = api_client.post(f'/api/orders/{order.order_number}/cancel/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND  # or 403