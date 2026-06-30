from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.orders.models.cart import Cart
from apps.orders.models.order import Order
from apps.orders.models.orderitem import OrderItem
from apps.orders.models.orderstatuslog import OrderStatusLog
from apps.orders.validators.checkout import CheckoutValidator


class CheckoutService:

    SHIPPING_FEE = Decimal('50.00')
    TAX_RATE = Decimal('0.10')
    
    @classmethod
    @transaction.atomic
    def process(cls, user, checkout_data: dict) -> Order:

        # ── STEP 1: VALIDATE ──
        cart = CheckoutValidator.validate_cart(user)
        CheckoutValidator.validate_address(checkout_data)
        CheckoutValidator.validate_stock(cart)  # Only checks availability, doesn't deduct
        
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
        
        # ── STEP 4: CREATE ORDER ITEMS (NO STOCK DEDUCTION) ──
        for cart_item in cart.items.select_related('product'):
            product = cart_item.product
            
            # Snapshot product data
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                product_name=product.name,
                product_price=product.price,
                quantity=cart_item.quantity,
                subtotal=product.price * cart_item.quantity
            )
        
        if not order.items.exists():
            raise ValidationError("Order must contain at least one item.")
        
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