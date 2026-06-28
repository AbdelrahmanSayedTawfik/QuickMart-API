from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import stripe

from apps.orders.models.order import Order
from apps.payments.serializers.payment import PaymentIntentResponseSerializer
from apps.payments.services.stripe import StripeService
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


@extend_schema(
    tags=['Payments'],
    summary='Create Stripe Checkout Session (Hosted)',
    description='Redirect user to Stripe-hosted checkout page. Best for web.',
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hosted_checkout(request, order_number):
    """Stripe hosts the payment form. Frontend redirects to checkout_url."""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    
    result = StripeService.create_checkout_session(order, request)
    
    return Response({
        'type': 'hosted',
        'checkout_url': result['checkout_url'],
        'session_id': result['session_id'],
    })
