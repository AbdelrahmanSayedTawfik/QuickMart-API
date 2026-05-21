from django.shortcuts import render
import stripe
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Payment
from apps.orders.models import Order



# Create your views here.


# apps/payments/views.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order_number = request.data.get('order_number')

    if not order_number:
        return Response(
            {'error': 'Order number is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.status == 'paid':
        return Response(
            {'error': 'Order is already paid.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),
            currency='usd',
            metadata={
                'order_number': order.order_number,
                'user_id': request.user.id
            }
        )
    except stripe.error.StripeError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # FIX: Use intent.id and intent.client_secret (attribute access, not dict access)
    # This works with both real Stripe response AND MagicMock in tests
    intent_id = intent.id                     # ← was intent['id']
    intent_secret = intent.client_secret      # ← was intent['client_secret']

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={                            # ← use defaults! not positional args
            'stripe_payment_intent_id': intent_id,
            'amount': order.total,
            'currency': 'usd',
            'status': 'pending',
        }
    )

    if not created:
        payment.stripe_payment_intent_id = intent_id    # ← fix variable name
        payment.save(update_fields=['stripe_payment_intent_id'])  # ← fix method name

    return Response({
        'client_secret': intent_secret,
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'amount': float(order.total),
        'order_number': order.order_number,
    }, status=status.HTTP_200_OK)
    
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the raw request body
    payload = request.body

    # Get Stripe's signature from headers
    # Stripe signs every webhook so you know it's really from Stripe
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        return HttpResponse('No signature', status=400)

    # Verify the webhook came from Stripe (not a fake request)
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET  # your webhook secret from Stripe dashboard
        )
    except ValueError:
        # Invalid payload
        return HttpResponse('Invalid payload', status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature - request didn't come from Stripe
        return HttpResponse('Invalid signature', status=400)

    # Handle different event types
    event_type = event['type']
    data = event['data']['object']

    # ── PAYMENT SUCCEEDED ──
    if event_type == 'payment_intent.succeeded':
        order_number = data['metadata'].get('order_number')

        try:
            order = Order.objects.get(order_number=order_number)

            # Update order status
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save(update_fields=['status', 'paid_at'])

            # Update payment record
            payment = order.payment
            payment.status = 'succeeded'
            payment.stripe_charge_id = data.get('latest_charge', '')
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'stripe_charge_id', 'paid_at'])

            # TODO: Send email (add Celery later)
            from apps.orders.tasks import send_payment_confirmation
            send_payment_confirmation.delay(order.id)

            print(f"✅ Payment succeeded for order {order_number}")

        except Order.DoesNotExist:
            print(f"❌ Order not found: {order_number}")
        except Payment.DoesNotExist:
            print(f"❌ Payment record not found for order: {order_number}")

    # ── PAYMENT FAILED ──
    elif event_type == 'payment_intent.payment_failed':
        order_number = data['metadata'].get('order_number')
        failure_message = data.get('last_payment_error', {}).get('message', 'Unknown error')

        try:
            order = Order.objects.get(order_number=order_number)
            payment = order.payment
            payment.status = 'failed'
            payment.failure_reason = failure_message
            payment.save(update_fields=['status', 'failure_reason'])

            print(f"❌ Payment failed for order {order_number}: {failure_message}")

        except (Order.DoesNotExist, Payment.DoesNotExist):
            pass

    # Always return 200 to Stripe
    # If you return anything else, Stripe will retry the webhook
    return HttpResponse(status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    try:
        payment = order.payment
        return Response({
            'order_number': order_number,
            'order_status': order.status,
            'payment_status': payment.status,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'paid_at': payment.paid_at,
            'stripe_payment_intent_id': payment.stripe_payment_intent_id,
        })
    except Payment.DoesNotExist:
        return Response({
            'order_number': order_number,
            'order_status': order.status,
            'payment_status': 'no_payment_found',
        })