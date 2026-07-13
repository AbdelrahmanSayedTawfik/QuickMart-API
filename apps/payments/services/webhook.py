import stripe
from django.conf import settings

from apps.orders.models.order import Order
from apps.payments.models.payment import Payment
from apps.orders.services.order import OrderService


class WebhookService:

    @staticmethod
    def construct_event(payload: bytes, sig_header: str):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

    @staticmethod
    def handle_event(event: dict) -> str:
        event_type = event.get('type', '')
        data = event.get('data', {}).get('object', {})

        handlers = {
            'payment_intent.succeeded': WebhookService._handle_payment_succeeded,
            'payment_intent.payment_failed': WebhookService._handle_payment_failed,
            'payment_intent.created': WebhookService._handle_payment_created,
            'charge.refunded': WebhookService._handle_refund,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                return handler(data)
            except Exception as e:
                return f'Error processing {event_type}: {str(e)}'

        return f'Unhandled event type: {event_type}'

    @staticmethod
    def _handle_payment_succeeded(data: dict) -> str:
        order_number = data.get('metadata', {}).get('order_number')
        charge_id = data.get('latest_charge', '')

        if not order_number:
            return 'No order_number in metadata'

        try:
            order = Order.objects.select_related('payment').get(order_number=order_number)

            # Already processed?
            if order.status != 'pending':
                return f'Order {order_number} already {order.status}, skipping'

            # CRITICAL: Check stock still available before deducting
            from apps.orders.validators.checkout import CheckoutValidator
            try:
                CheckoutValidator.validate_stock(order, order.delivery_city)
            except Exception as e:
                order.status = 'cancelled'
                order.save()
                return f'Order {order_number} cancelled: stock no longer available'

            # Update payment record
            payment = order.payment
            payment.stripe_charge_id = charge_id
            payment.status = 'succeeded'
            payment.save()

            # Mark order paid (deducts stock, creates movements)
            OrderService.mark_as_paid(order)

            # Send confirmation email
            try:
                from apps.orders.tasks.emails import send_payment_confirmation
                send_payment_confirmation.delay(order.id)
            except Exception:
                pass

            return f'Payment succeeded for order {order_number}'

        except Order.DoesNotExist:
            return f'Order not found: {order_number}'
        except Payment.DoesNotExist:
            return f'Payment record not found: {order_number}'
        except Exception as e:
            return f'Error: {str(e)}'

    @staticmethod
    def _handle_payment_failed(data: dict) -> str:
        order_number = data.get('metadata', {}).get('order_number')
        failure_message = data.get('last_payment_error', {}).get('message', 'Unknown error')

        if not order_number:
            return 'No order_number in metadata'

        try:
            order = Order.objects.select_related('payment').get(order_number=order_number)
            payment = order.payment
            payment.status = 'failed'
            payment.failure_reason = failure_message
            payment.save()
            return f'Payment failed for {order_number}: {failure_message}'
        except Exception as e:
            return f'Error: {str(e)}'

    @staticmethod
    def _handle_payment_created(data: dict) -> str:
        order_number = data.get('metadata', {}).get('order_number')
        return f'Payment intent created for {order_number or "unknown"}'

    @staticmethod
    def _handle_refund(data: dict) -> str:
        payment_intent = data.get('payment_intent')

        if not payment_intent:
            return 'No payment_intent in refund data'

        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent)
            payment.status = 'refunded'
            payment.save()

            order = payment.order
            if order.status in ('paid', 'shipped', 'delivered'):
                OrderService.update_status(order, 'refunded')

            return f'Payment refunded: {payment_intent}'
        except Exception as e:
            return f'Error: {str(e)}'