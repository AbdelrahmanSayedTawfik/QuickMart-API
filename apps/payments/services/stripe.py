import stripe
from django.conf import settings

from apps.orders.models.order import Order
from apps.payments.models.payment import Payment
from apps.payments.validators.payment import PaymentValidator


class StripeService:

    @staticmethod
    def _configure_api():
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    @staticmethod
    def create_payment_intent(order: Order) -> dict:

        StripeService._configure_api()
        
        # Validate order can be paid
        PaymentValidator.validate_order_not_paid(order)
        PaymentValidator.validate_order_pending(order)
        
        # Create PaymentIntent on Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Stripe uses cents
            currency='usd',
            metadata={
                'order_number': order.order_number,
                'user_id': order.user.id,
                'order_id': order.id
            },
            # Optional: automatic payment methods
            automatic_payment_methods={'enabled': True}
        )
        
        # Create or update local payment record
        payment, created = Payment.objects.update_or_create(
            order=order,
            defaults={
                'stripe_payment_intent_id': intent.id,
                'amount': order.total,
                'currency': 'usd',
                'status': 'pending',
            }
        )
        
        return {
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'amount': float(order.total),
            'order_number': order.order_number,
        }
        
    @staticmethod
    def create_checkout_session(order: Order, request) -> dict:
        StripeService._configure_api()
        
        PaymentValidator.validate_order_not_paid(order)
        PaymentValidator.validate_order_pending(order)
        
        response_format = request.data.get('response_format', 'redirect')
    
        success_url = request.build_absolute_uri(
            f'/api/payments/success/?order_number={order.order_number}&format={response_format}'
        )
        cancel_url = request.build_absolute_uri(
            f'/api/payments/cancel/?order_number={order.order_number}&format={response_format}'
        )
        
        # Build line items from order items
        line_items = []
        for item in order.items.select_related('product'):
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product_name,
                        'images': (
                            [item.product.images.first().image.url]
                            if item.product.images.exists()
                            else []
                        ),
                    },
                    'unit_amount': int(item.product_price * 100),
                },
                'quantity': item.quantity,
            })
        
        # Add shipping if applicable
        if order.shipping_fee and order.shipping_fee > 0:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Shipping Fee'},
                    'unit_amount': int(order.shipping_fee * 100),
                },
                'quantity': 1,
            })
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_number': order.order_number,
                'order_id': order.id,
            },
            payment_intent_data={
                'metadata': {
                    'order_number': order.order_number,
                }
            },
        )
        
        Payment.objects.update_or_create(
            order=order,
            defaults={
                'stripe_payment_intent_id': session.payment_intent,
                'stripe_checkout_session_id': session.id,
                'amount': order.total,
                'currency': 'usd',
                'status': 'pending',
            }
        )
        
        return {
            'checkout_url': session.url,
            'session_id': session.id,
            'order_number': order.order_number,
        }    
    
    @staticmethod
    def retrieve_payment_intent(intent_id: str):
        
        StripeService._configure_api()
        return stripe.PaymentIntent.retrieve(intent_id)
    
    @staticmethod
    def cancel_payment_intent(intent_id: str):
        
        StripeService._configure_api()
        return stripe.PaymentIntent.cancel(intent_id)


class PaymentRecordService:

    
    @staticmethod
    def get_or_create_for_order(order: Order, intent_id: str) -> Payment:

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'stripe_payment_intent_id': intent_id,
                'amount': order.total,
                'currency': 'usd',
                'status': 'pending',
            }
        )
        
        if not created:
            # Update intent ID if changed
            payment.stripe_payment_intent_id = intent_id
            payment.save(update_fields=['stripe_payment_intent_id'])
        
        return payment
    
    @staticmethod
    def mark_succeeded(order: Order, charge_id: str = None) -> Payment:

        from apps.orders.services.order import OrderService
        
        payment = order.payment
        payment.mark_as_succeeded(charge_id)
        
        # Update order status via OrderService
        OrderService.mark_as_paid(order)
        
        return payment
    
    @staticmethod
    def mark_failed(order: Order, reason: str = None) -> Payment:

        payment = order.payment
        payment.mark_as_failed(reason)
        return payment