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
    summary='Create Stripe payment intent',
    description='''
    Initializes a Stripe PaymentIntent for an order.
    
    **Flow:**
    1. Frontend calls this endpoint with order_number
    2. Backend creates PaymentIntent on Stripe
    3. Backend returns client_secret to frontend
    4. Frontend uses Stripe.js to collect card details
    5. Stripe processes payment and sends webhook
    
    **Prevents double-payment** for already-paid orders.
    ''',
    request=None,
    responses={
        200: OpenApiResponse(
            description='Payment intent created',
            response=PaymentIntentResponseSerializer
        ),
        400: OpenApiResponse(description='Order number missing or already paid'),
        404: OpenApiResponse(description='Order not found'),
        500: OpenApiResponse(description='Stripe API error'),
    },
    examples=[
        OpenApiExample(
            'Request',
            value={'order_number': 'QM-ABC123DEF456'},
            request_only=True,
        ),
        OpenApiExample(
            'Success Response',
            value={
                'client_secret': 'pi_3Oxxx_secret_Sxxx',
                'publishable_key': 'pk_test_51xxx',
                'amount': 150.00,
                'order_number': 'QM-ABC123DEF456',
            },
            response_only=True,
        ),
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):

    order_number = request.data.get('order_number')
    
    if not order_number:
        return Response(
            {'error': 'Order number is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get order (must belong to current user)
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )
    
    # Delegate to service
    try:
        result = StripeService.create_payment_intent(order)
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Stripe error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(result, status=status.HTTP_200_OK)