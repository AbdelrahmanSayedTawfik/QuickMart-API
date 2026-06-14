from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from apps.orders.models.order import Order


@extend_schema(
    tags=['Payments'],
    summary='Check payment status',
    description='Retrieves the current payment status for a specific order.',
    parameters=[
        OpenApiParameter(
            name='order_number',
            type=str,
            location=OpenApiParameter.PATH,
            description='Order number to check payment for'
        ),
    ],
    responses={
        200: OpenApiResponse(
            description='Payment status retrieved',
            response={
                'order_number': 'QM-ABC123DEF456',
                'order_status': 'paid',
                'payment_status': 'succeeded',
                'amount': 150.00,
                'currency': 'usd',
                'paid_at': '2024-01-15T10:30:00Z',
                'stripe_payment_intent_id': 'pi_3Oxxx',
            }
        ),
        404: OpenApiResponse(description='Order or payment not found'),
    }
)
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
    except Order.payment.RelatedObjectDoesNotExist:
        # No payment record yet
        return Response({
            'order_number': order_number,
            'order_status': order.status,
            'payment_status': 'no_payment_initiated',
        })