import stripe
from django.conf import settings
from django.utils import timezone

from apps.orders.models.order import Order
from apps.payments.models.payment import Payment
from apps.payments.validators.payment import PaymentValidator
from apps.payments.services.stripe import PaymentRecordService


class WebhookService:

    @staticmethod
    def construct_event(payload: bytes, sig_header: str):

        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        return PaymentValidator.validate_webhook_signature(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    
    @staticmethod
    def handle_event(event: dict) -> str:

        event_type = event['type']
        data = event['data']['object']
        
        handlers = {
            'payment_intent.succeeded': WebhookService._handle_payment_succeeded,
            'payment_intent.payment_failed': WebhookService._handle_payment_failed,
            'payment_intent.created': WebhookService._handle_payment_created,
            'charge.refunded': WebhookService._handle_refund,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(data)
        
        return f'Unhandled event type: {event_type}'
    
    @staticmethod
    def _handle_payment_succeeded(data: dict) -> str:

        order_number = data['metadata'].get('order_number')
        
        try:
            order = Order.objects.select_related('payment').get(order_number=order_number)
            charge_id = data.get('latest_charge', '')
            
            # Update payment and order
            PaymentRecordService.mark_succeeded(order, charge_id)
            
            # Send confirmation email (Celery task)
            from apps.orders.tasks.emails import send_payment_confirmation
            send_payment_confirmation.delay(order.id)
            
            return f'Payment succeeded for order {order_number}'
            
        except Order.DoesNotExist:
            return f'Order not found: {order_number}'
        except Payment.DoesNotExist:
            return f'Payment record not found for order: {order_number}'
        except Exception as e:
            return f'Error processing payment success: {str(e)}'
    
    @staticmethod
    def _handle_payment_failed(data: dict) -> str:

        order_number = data['metadata'].get('order_number')
        failure_message = data.get('last_payment_error', {}).get('message', 'Unknown error')
        
        try:
            order = Order.objects.select_related('payment').get(order_number=order_number)
            PaymentRecordService.mark_failed(order, failure_message)
            
            return f'Payment failed for order {order_number}: {failure_message}'
            
        except (Order.DoesNotExist, Payment.DoesNotExist):
            return f'Order/Payment not found: {order_number}'
        except Exception as e:
            return f'Error processing payment failure: {str(e)}'
    
    @staticmethod
    def _handle_payment_created(data: dict) -> str:

        return 'Payment intent created (no action needed)'
    
    @staticmethod
    def _handle_refund(data: dict) -> str:

        payment_intent = data.get('payment_intent')
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent)
            payment.status = 'refunded'
            payment.save(update_fields=['status'])
            
            return f'Payment refunded: {payment_intent}'
            
        except Payment.DoesNotExist:
            return f'Payment not found for refund: {payment_intent}'