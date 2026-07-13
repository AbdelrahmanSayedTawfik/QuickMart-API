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

        # ── STEP 1: VALIDATE ORDER STATUS ──
        if order.status != 'pending':
            raise ValidationError(f"Order is already {order.status}. Cannot mark as paid.")

        # ── STEP 2: LOCK PRODUCTS & VALIDATE STOCK (fail-fast pre-check) ──
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

        # ── STEP 3: MARK ORDER AS PAID (delegates real deduction to InventoryService) ──
        from apps.orders.services.order import OrderService
        OrderService.mark_as_paid(order)

        # ── STEP 4: GET OR CREATE PAYMENT RECORD ──
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total,
                'currency': 'usd',
                'status': 'succeeded',
            }
        )

        if not created:
            payment.status = 'succeeded'
            payment.save()

        if not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save()

        return order