# ═══════════════════════════════════════════════════════════════
# apps/products/tests/test_products.py
# ═══════════════════════════════════════════════════════════════

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestProductList:
    """
    Tests for GET /api/products/
    """
    
    def test_list_products_public(self, api_client, product):
        """
        Test: Anyone can list products (no auth needed).
        
        product: Fixture that creates a test product
        """
        response = api_client.get('/api/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
        assert response.data['results'][0]['name'] == 'Test Iphone 14 Pro Max'
    
    def test_filter_by_category(self, api_client, product, category):
        """
        Test: Filter products by category slug.
        """
        response = api_client.get(f'/api/products/?category={category.slug}')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Test Iphone 14 Pro Max'
    
    def test_filter_by_price_range(self, api_client, product):
        """
        Test: Filter products by min/max price.
        """
        response = api_client.get('/api/products/?min_price=500&max_price=1500')
        
        assert response.status_code == status.HTTP_200_OK
        for item in response.data['results']:
            price = float(item['price'])
            assert 500 <= price <= 1500
    
    def test_search_by_name(self, api_client, product):
        """
        Test: Search products by name.
        """
        response = api_client.get('/api/products/?search=iPhone')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert 'Iphone' in response.data['results'][0]['name']
    
    def test_order_by_price(self, api_client, product):
        """
        Test: Order products by price ascending/descending.
        """
        # Ascending
        response = api_client.get('/api/products/?ordering=price')
        assert response.status_code == status.HTTP_200_OK
        
        # Descending
        response = api_client.get('/api/products/?ordering=-price')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestProductCreate:
    """
    Tests for POST /api/products/
    """
    
    def test_create_product_as_seller(self, seller_auth_client, category):
        """
        Test: Seller can create products.
        
        seller_auth_client: Authenticated as seller
        """
        payload = {
            'name': 'MacBook Pro',
            'slug': 'macbook-pro',
            'description': 'Powerful laptop',
            'price': 1999.99,
            'original_price': 2199.99,
            'stock_quantity': 10,
            'category': category.id,
            'status': 'available',
            'sku': 'MBP-2024-001',  
        }
        
        response = seller_auth_client.post('/api/products/', payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'MacBook Pro'
        assert response.data['seller'] == seller_auth_client.handler._force_user.id

    
    def test_create_product_as_customer_fails(self, auth_client, category):
        """
        Test: Customer cannot create products (403 Forbidden).
        
        auth_client: Authenticated as customer
        """
        payload = {
            'name': 'MacBook Pro',
            'slug': 'macbook-pro',
            'price': 1999.99,
            'stock_quantity': 10,
            'category': category.id,
        }
        
        response = auth_client.post('/api/products/', payload, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_product_unauthenticated_fails(self, api_client, category):
        """
        Test: Anonymous user cannot create products.
        """
        payload = {
            'name': 'MacBook Pro',
            'slug': 'macbook-pro',
            'price': 1999.99,
            'stock_quantity': 10,
            'category': category.id,
        }
        
        response = api_client.post('/api/products/', payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProductDetail:
    """
    Tests for GET /api/products/{slug}/
    """
    
    def test_retrieve_product(self, api_client, product):
        """
        Test: Get single product by slug.
        """
        response = api_client.get(f'/api/products/{product.slug}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name
        assert response.data['slug'] == product.slug
    
    def test_update_product_as_owner(self, seller_auth_client, product):
        """
        Test: Product owner can update their product.
        """
        response = seller_auth_client.patch(f'/api/products/{product.slug}/', {
            'price': 899.99
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['price']) == 899.99
    
    def test_update_product_as_non_owner_fails(self, auth_client, product):
        """
        Test: Non-owner cannot update product.
        """
        response = auth_client.patch(f'/api/products/{product.slug}/', {
            'price': 1.00
        }, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN