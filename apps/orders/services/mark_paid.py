from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.orders.models.order import Order
from apps.payments.models.payment import Payment
from apps.inventory.models.stock_movement import StockMovement
from apps.orders.models.orderstatuslog import OrderStatusLog
from apps.inventory.services.alert import AlertService


class MarkOrderPaidService:

    @classmethod
    @transaction.atomic
    def process(cls, user, order: Order) -> Order:
        """
        Mark order as paid and deduct stock. ALL or NOTHING.
        """
        # ── STEP 1: VALIDATE ORDER STATUS ──
        if order.status != 'pending':
            raise ValidationError(f"Order is already {order.status}. Cannot mark as paid.")

        # ── STEP 2: LOCK PRODUCTS & VALIDATE STOCK ──
        from apps.products.models import Product
        
        product_ids = list(order.items.values_list('product_id', flat=True))
        locked_products = {
            p.id: p 
            for p in Product.objects.filter(id__in=product_ids).select_for_update()
        }
        
        for item in order.items.all():
            product = locked_products.get(item.product_id)
            if not product:
                raise ValidationError(f"Product {item.product_id} no longer exists.")
            
            if product.stock_quantity < item.quantity:
                raise ValidationError(
                    f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}, Required: {item.quantity}"
                )

        # ── STEP 3: MARK ORDER AS PAID ──
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

        # ── STEP 4: DEDUCT STOCK ──
        for item in order.items.all():
            product = locked_products[item.product_id]
            previous_stock = product.stock_quantity

            product.stock_quantity -= item.quantity
            product.save()

            StockMovement.objects.create(
                product=product,
                movement_type='out',
                quantity=item.quantity,
                previous_stock=previous_stock,
                new_stock=product.stock_quantity,
                reason=f'Order {order.order_number}',
                created_by=user
            )

            AlertService.check_and_create_alerts(product)

        # ── STEP 5: GET OR CREATE PAYMENT RECORD ──
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total,
                'currency': 'usd',
                'status': 'succeeded',
            }
        )

        if not created:
            # Payment already existed, just update status
            payment.status = 'succeeded'
            payment.save()

        # Always update paid_at (whether created or existing)
        if not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save()

        # ── STEP 6: LOG STATUS CHANGE ──
        OrderStatusLog.objects.create(
            order=order,
            previous_status='pending',
            new_status='paid',
            created_by=user
        )

        return order