from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.payments.services.webhook import WebhookService


@extend_schema(
    tags=['Payments'],
    summary='Stripe webhook handler',
    description='''
    Receives asynchronous events from Stripe.
    
    **Events handled:**
    - `payment_intent.succeeded` — Payment confirmed, update order
    - `payment_intent.payment_failed` — Card declined, log reason
    - `charge.refunded` — Refund processed
    
    **Security:**
    - Verifies Stripe signature to ensure request is from Stripe
    - Must return 200 OK — otherwise Stripe retries
    
    **Called by:** Stripe (not your frontend)
    ''',
    request=None,
    responses={
        200: OpenApiResponse(description='Webhook processed'),
        400: OpenApiResponse(description='Invalid payload or signature'),
    }
)
@csrf_exempt  # Stripe doesn't send CSRF token
def stripe_webhook(request):

    # Get raw request body (bytes, not parsed JSON)
    payload = request.body
    
    # Get Stripe's signature from headers
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Verify and parse event
    try:
        event = WebhookService.construct_event(payload, sig_header)
    except Exception as e:
        return HttpResponse(str(e), status=400)
    
    # Process the event
    result = WebhookService.handle_event(event)
    
    # Always return 200 to Stripe
    # If we return error, Stripe retries the webhook
    return HttpResponse(result, status=200)