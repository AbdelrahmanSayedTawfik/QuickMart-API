from django.core.exceptions import ValidationError
from apps.orders.models.order import Order


class PaymentValidator:

    @staticmethod
    def validate_order_not_paid(order: Order) -> None:
        """
        Prevent double-payment.
        """
        if order.status == 'paid':
            raise ValidationError('Order is already paid.')
        
        # Also check payment record
        if hasattr(order, 'payment') and order.payment.is_paid:
            raise ValidationError('Payment already completed for this order.')
    
    @staticmethod
    def validate_order_ownership(order: Order, user) -> None:

        if order.user != user:
            raise ValidationError('You do not have permission to pay for this order.')
    
    @staticmethod
    def validate_order_pending(order: Order) -> None:

        if order.status != 'pending':
            raise ValidationError(
                f'Cannot process payment for order with status: {order.status}. '
                f'Only pending orders can be paid.'
            )
    
    @staticmethod
    def validate_webhook_signature(payload: bytes, sig_header: str, secret: str):

        import stripe
        
        if not sig_header:
            raise ValidationError('No Stripe signature header found.')
        
        try:
            return stripe.Webhook.construct_event(payload, sig_header, secret)
        except ValueError:
            raise ValidationError('Invalid payload.')
        except stripe.error.SignatureVerificationError:
            raise ValidationError('Invalid signature. Request may not be from Stripe.')