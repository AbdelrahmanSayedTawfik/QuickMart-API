from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.orders.models.cart import Cart
from apps.orders.models.order import Order
from apps.orders.models.orderitem import OrderItem
from apps.orders.models.orderstatuslog import OrderStatusLog
from apps.orders.validators.checkout import CheckoutValidator
from apps.inventory.services.stock import InventoryService


class CheckoutService:
    """
    THE MOST IMPORTANT service in the orders app.
    
    Converts a cart into an order. This is "business logic" —
    the rules of HOW shopping works:
    
    1. Validate everything first (fail fast)
    2. Create the order
    3. Create order items (snapshot prices)
    4. Deduct stock (via InventoryService)
    5. Clear cart
    6. Send notifications
    
    The API view just calls this. No logic in the view!
    """
    
    SHIPPING_FEE = Decimal('50.00')
    TAX_RATE = Decimal('0.10')
    
    @classmethod
    @transaction.atomic
    def process(cls, user, checkout_data: dict) -> Order:
        """
        Main checkout flow. ALL or NOTHING.
        
        If ANY step fails, the ENTIRE transaction rolls back.
        Customer doesn't get charged for a failed order.
        Stock doesn't get deducted for a failed order.
        
        Args:
            user: The customer
            checkout_data: {
                'delivery_address': '123 Main St',
                'delivery_city': 'New York',
                'delivery_phone': '+1234567890',
                'notes': 'Leave at door'
            }
        
        Returns:
            The created Order
        
        Raises:
            ValidationError: If cart empty, stock insufficient, etc.
        """
        # ── STEP 1: VALIDATE ──
        cart = CheckoutValidator.validate_cart(user)
        CheckoutValidator.validate_address(checkout_data)
        CheckoutValidator.validate_stock(cart)
        
        # ── STEP 2: CALCULATE TOTALS ──
        subtotal = cart.total
        tax = subtotal * cls.TAX_RATE
        total = subtotal + tax + cls.SHIPPING_FEE
        
        # ── STEP 3: CREATE ORDER ──
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            tax=tax,
            total=total,
            shipping_fee=cls.SHIPPING_FEE,
            delivery_address=checkout_data['delivery_address'],
            delivery_city=checkout_data['delivery_city'],
            delivery_phone=checkout_data['delivery_phone'],
            notes=checkout_data.get('notes', ''),
            status='pending'
        )
        
        # ── STEP 4: CREATE ORDER ITEMS + DEDUCT STOCK ──
        for cart_item in cart.items.select_related('product'):
            product = cart_item.product
            
            # Snapshot product data (price won't change even if product updated later)
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                product_name=product.name,
                product_price=product.price,
                quantity=cart_item.quantity,
                subtotal=product.price * cart_item.quantity
            )
            
            # Deduct stock using InventoryService (creates audit trail!)
            InventoryService.deduct_stock(
                product=product,
                quantity=cart_item.quantity,
                reason=f'Order {order.order_number}',
                user=user,
                order=order
            )
        
        # ── STEP 5: CLEAR CART ──
        cart.items.all().delete()
        
        # ── STEP 6: LOG STATUS CHANGE ──
        OrderStatusLog.objects.create(
            order=order,
            previous_status='',
            new_status='pending',
            created_by=user
        )
        
        return order