from django.db import transaction
from django.utils import timezone

from apps.orders.models.order import Order
from apps.orders.models.orderstatuslog import OrderStatusLog
from apps.inventory.services.stock import InventoryService
from apps.orders.services.notification import NotificationService


class OrderService:

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order, user) -> None:

        if order.status not in ('pending', 'paid'):
            raise ValueError(f'Cannot cancel order with status: {order.status}')
        
        # Only restore stock if payment was already processed
        if order.status == 'paid':
            for item in order.items.select_related('product'):
                if item.product:
                    InventoryService.return_stock(
                        product=item.product,
                        quantity=item.quantity,
                        reason=f'Order cancelled (refund): {order.order_number}',
                        user=user,
                        order=order
                    )
        
        # Update order status
        old_status = order.status
        order.status = 'cancelled'
        order.save()
        
        # Log the change
        OrderStatusLog.objects.create(
            order=order,
            previous_status=old_status,
            new_status='cancelled',
            created_by=user
        )
        
        # Notify customer
        NotificationService.notify_order_cancelled(order)
    
    @staticmethod
    @transaction.atomic
    def mark_as_paid(order: Order) -> None:

        if order.status != 'pending':
            return  # Already processed or wrong status
        
        # Deduct stock for each item (FIRST TIME!)
        for item in order.items.select_related('product'):
            if item.product:
                InventoryService.deduct_stock(
                    product=item.product,
                    quantity=item.quantity,
                    reason=f'Order paid: {order.order_number}',
                    user=order.user,
                    order=order
                )
        
        old_status = order.status
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        OrderStatusLog.objects.create(
            order=order,
            previous_status=old_status,
            new_status='paid'
        )
        
        # Notify customer
        NotificationService.notify_payment_confirmed(order)
    
    @staticmethod
    @transaction.atomic
    def update_status(order: Order, new_status: str, user=None) -> None:

        valid_transitions = {
            'pending': ['paid', 'cancelled'],
            'paid': ['processing', 'refunded', 'cancelled'],
            'processing': ['shipped'],
            'shipped': ['delivered'],
            'delivered': ['refunded'],
        }
        
        allowed = valid_transitions.get(order.status, [])
        if new_status not in allowed:
            raise ValueError(
                f'Cannot transition from {order.status} to {new_status}. '
                f'Allowed: {", ".join(allowed)}'
            )
        
        old_status = order.status
        
        # Handle stock for specific transitions
        if new_status == 'cancelled' and old_status == 'paid':
            # Paid order being cancelled — restore stock
            for item in order.items.select_related('product'):
                if item.product:
                    InventoryService.return_stock(
                        product=item.product,
                        quantity=item.quantity,
                        reason=f'Order cancelled (refund): {order.order_number}',
                        user=user,
                        order=order
                    )
        
        order.status = new_status
        
        # Set timestamps based on status
        if new_status == 'shipped':
            order.shipped_at = timezone.now()
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
        
        order.save()
        
        OrderStatusLog.objects.create(
            order=order,
            previous_status=old_status,
            new_status=new_status,
            created_by=user
        )
        
        NotificationService.notify_status_update(order, old_status, new_status)