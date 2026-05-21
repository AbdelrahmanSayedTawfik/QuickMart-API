# apps/conftest.py — COMPLETE FIXED VERSION

import pytest
from rest_framework.test import APIClient
from apps.accounts.models import CustomUser
from apps.products.models import Category, Product
from apps.orders.models import Cart, CartItem, Order, OrderItem
from decimal import Decimal


# ─────────────────────────────────────────────────────────────
# CLIENT FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


# ─────────────────────────────────────────────────────────────
# USER FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def create_user(db):
    """Creates a basic customer user."""
    return CustomUser.objects.create_user(
        username='testuser',
        password='testpass',
        email='test@example.com',
        role='customer'
    )


# FIX: Tests use 'customer_user' — add this fixture
@pytest.fixture
def customer_user(db):
    """
    Creates a customer user for authentication tests.
    Tests reference: customer_user.email, username='customer1'
    """
    return CustomUser.objects.create_user(
        username='customer1',
        password='Test@1234',
        email='customer@example.com',
        role='customer'
    )


@pytest.fixture
def seller_user(db):
    """Creates a seller user."""
    return CustomUser.objects.create_user(
        username='selleruser',
        password='sellerpass',
        email='seller@example.com',
        role='seller'
    )


@pytest.fixture
def admin_user(db):
    """Creates an admin user."""
    return CustomUser.objects.create_superuser(
        username='adminuser',
        password='adminpass',
        email='admin@example.com',
        role='admin'
    )


# ─────────────────────────────────────────────────────────────
# AUTHENTICATED CLIENT FIXTURES
# Define BOTH the old names AND the short names tests use
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def authenticated_client(api_client, customer_user):
    """Authenticated as customer. Old name kept for backward compatibility."""
    api_client.force_authenticate(user=customer_user)
    return api_client


# FIX: Tests use 'auth_client' — add this alias
@pytest.fixture
def auth_client(api_client, customer_user):
    """
    Authenticated APIClient as customer.
    This is what test files reference as 'auth_client'.
    """
    api_client.force_authenticate(user=customer_user)
    return api_client


@pytest.fixture
def seller_authenticated_client(api_client, seller_user):
    """Authenticated as seller. Old name kept for backward compatibility."""
    api_client.force_authenticate(user=seller_user)
    return api_client


# FIX: Tests use 'seller_auth_client' — add this alias
@pytest.fixture
def seller_auth_client(api_client, seller_user):
    """
    Authenticated APIClient as seller.
    This is what test files reference as 'seller_auth_client'.
    """
    api_client.force_authenticate(user=seller_user)
    return api_client


# ─────────────────────────────────────────────────────────────
# PRODUCT FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def category(db):
    """Creates a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category',
        description='A category for testing.'
    )


@pytest.fixture
def product(db, seller_user, category):
    """
    Creates a test product.

    FIX: Added original_price=None (null=True, blank=True in model)
    OR added original_price value to avoid NOT NULL constraint.

    Check your Product model:
    - If original_price has null=True → pass original_price=None
    - If original_price has no null=True → pass a value
    """
    return Product.objects.create(
        name='Test Iphone 14 Pro Max',
        slug='test-iphone-14-pro-max',
        description='An iPhone 14 Pro Max for testing.',
        price=Decimal('999.99'),
        original_price=Decimal('1099.99'),  # FIX: Added this line
        stock_quantity=100,
        status='available',
        category=category,
        seller=seller_user,
        is_active=True,
    )


@pytest.fixture
def out_of_stock_product(db, seller_user, category):
    """Creates a product with zero stock."""
    return Product.objects.create(
        name='Test Out of Stock Product',
        slug='test-out-of-stock-product',
        description='A product that is out of stock for testing.',
        price=Decimal('49.99'),
        original_price=Decimal('59.99'),  # FIX: Added this line
        stock_quantity=0,
        status='out_of_stock',
        category=category,
        seller=seller_user,
        is_active=True,
    )


# ─────────────────────────────────────────────────────────────
# CART & ORDER FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def cart(db, customer_user):
    """Creates a cart for the customer user."""
    # Try get_or_create because signal might already create it
    cart, _ = Cart.objects.get_or_create(user=customer_user)
    return cart


@pytest.fixture
def cart_item(db, cart, product):
    """Creates a cart item with quantity 2."""
    return CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )


# FIX: Tests use 'cart_with_items' — add this fixture
@pytest.fixture
def cart_with_items(db, customer_user, product):
    """
    Creates a cart WITH items already in it.
    Used by checkout and cart removal tests.

    Different from 'cart_item' because tests need the cart
    to already have items when the test starts.
    """
    cart, _ = Cart.objects.get_or_create(user=customer_user)

    # Clear any existing items first
    cart.items.all().delete()

    # Add the product
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=2
    )
    return cart


@pytest.fixture
def order(db, customer_user):
    """
    Creates a test order for customer_user.

    FIX: Uses customer_user (not create_user) to match auth_client fixture.
    auth_client authenticates as customer_user.
    If order belongs to create_user, auth_client can't see it.
    """
    return Order.objects.create(
        user=customer_user,
        order_number='QM-TESTORDER1',
        subtotal=Decimal('199.98'),
        tax=Decimal('19.99'),
        shipping_fee=Decimal('20.00'),
        discount=Decimal('0.00'),
        total=Decimal('239.97'),
        delivery_address='123 Test St',
        delivery_city='Cairo',
        delivery_phone='01012345678',
        status='pending'
    )


"""
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest apps/orders/tests/test_orders.py

# Run specific test class
pytest apps/orders/tests/test_orders.py::TestCheckout

# Run specific test method
pytest apps/orders/tests/test_orders.py::TestCheckout::test_checkout_success

# Run with coverage report
pytest --cov=apps --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
# OR
xdg-open htmlcov/index.html  # Linux

"""    