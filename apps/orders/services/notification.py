from django.conf import settings

from apps.orders.tasks.emails import (
    send_order_confirmation_email,
    send_payment_confirmation,
    send_status_update
)


class NotificationService:

    @staticmethod
    def notify_order_created(order):
        
        # Email (async via Celery)
        try:
            send_order_confirmation_email.delay(order.id)
        except Exception:
            pass  # Don't fail order if email fails
        
        # WebSocket (real-time notification)
        NotificationService._send_websocket(order, 'created', 'Order created successfully.')
    
    @staticmethod
    def notify_payment_confirmed(order):
        
        try:
            send_payment_confirmation.delay(order.id)
        except Exception:
            pass
        
        NotificationService._send_websocket(order, 'paid', 'Payment confirmed!')
    
    @staticmethod
    def notify_status_update(order, old_status, new_status):
        
        try:
            send_status_update.delay(order.id, new_status)
        except Exception:
            pass
        
        NotificationService._send_websocket(
            order, new_status, f'Order status updated to {new_status}.'
        )
    
    @staticmethod
    def notify_order_cancelled(order):
        
        NotificationService._send_websocket(
            order, 'cancelled', 'Order cancelled successfully.'
        )
    
    @staticmethod
    def _send_websocket(order, new_status, message):

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from django.utils import timezone
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{order.user.id}_orders',
                {
                    'type': 'order_status_update',
                    'order_number': order.order_number,
                    'new_status': new_status,
                    'message': message,
                    'timestamp': str(timezone.now())
                }
            )
        except Exception:
            pass  # WebSocket is optional, don't fail if Redis down