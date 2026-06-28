# apps/payments/apis/success.py
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response


FRONTEND_URL = 'http://localhost:3000'  # Change for production


@api_view(['GET'])
def payment_success(request):
    
    order_number = request.GET.get('order_number')
    response_type = request.GET.get('format', 'redirect')  # Default: redirect
    
    # Option: JSON response
    if response_type == 'json':
        return Response({
            'status': 'success',
            'message': 'Payment successful!',
            'order_number': order_number,
            'redirect_url': f'{FRONTEND_URL}/payment-success?order={order_number}'
        })
    
    # Option: Redirect to frontend (default)
    return redirect(f'{FRONTEND_URL}/payment-success?order={order_number}')


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