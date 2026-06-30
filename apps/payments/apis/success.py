from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample


FRONTEND_URL = 'http://localhost:3000'

@extend_schema(
    tags=['Payments'],
    summary='Payment success callback',
    description='Called by Stripe after successful payment. Redirects to frontend or returns JSON.',
    parameters=[
        OpenApiParameter(name='order_number', type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='format', type=str, location=OpenApiParameter.QUERY, description="Pass 'json' to get JSON instead of redirect"),
    ],
    responses={
        200: OpenApiResponse(description='JSON response (when format=json)'),
        302: OpenApiResponse(description='Redirect to frontend success page (default)'),
    }
)
@api_view(['GET'])
def payment_success(request):
    order_number = request.GET.get('order_number')
    response_type = request.GET.get('format', 'redirect')

    if response_type == 'json':
        return Response({
            'status': 'success',
            'message': 'Payment successful!',
            'order_number': order_number,
            'redirect_url': f'{FRONTEND_URL}/payment-success?order={order_number}'
        })

    return redirect(f'{FRONTEND_URL}/payment-success?order={order_number}')


@extend_schema(
    tags=['Payments'],
    summary='Payment cancel callback',
    description='Called by Stripe when user cancels payment. Redirects to frontend or returns JSON.',
    parameters=[
        OpenApiParameter(name='order_number', type=str, location=OpenApiParameter.QUERY),
        OpenApiParameter(name='format', type=str, location=OpenApiParameter.QUERY, description="Pass 'json' to get JSON instead of redirect"),
    ],
    responses={
        200: OpenApiResponse(description='JSON response (when format=json)'),
        302: OpenApiResponse(description='Redirect to frontend cancel page (default)'),
    }
)
@api_view(['GET'])
def payment_cancel(request):
    order_number = request.GET.get('order_number')
    response_type = request.GET.get('format', 'redirect')

    if response_type == 'json':
        return Response({
            'status': 'cancelled',
            'message': 'Payment was cancelled.',
            'order_number': order_number,
            'retry_url': f'/api/payments/{order_number}/checkout/',
            'redirect_url': f'{FRONTEND_URL}/payment-cancelled?order={order_number}'
        })

    return redirect(f'{FRONTEND_URL}/payment-cancelled?order={order_number}')