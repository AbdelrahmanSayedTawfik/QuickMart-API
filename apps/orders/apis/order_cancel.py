from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample

from apps.orders.models.order import Order
from apps.orders.serializers.order import OrderSerializer
from apps.orders.services.order import OrderService
from apps.orders.services.notification import NotificationService


@extend_schema(
    tags=['Orders'],
    summary='Cancel order',
    description='''
    Cancels a pending or paid order.
    
    **What happens:**
    - If order is **pending**: Just cancels — no stock was deducted
    - If order is **paid**: Cancels and restores product stock quantities
    - Logs status change
    - Sends WebSocket notification
    ''',
    parameters=[
        OpenApiParameter(
            name='order_number',
            type=str,
            location=OpenApiParameter.PATH,
            description='Order number to cancel'
        ),
    ],
    responses={
        200: OpenApiResponse(
            description='Order cancelled successfully',
            examples=[OpenApiExample('Success', value={'message': 'Order cancelled successfully.'})]
        ),
        400: OpenApiResponse(description='Order cannot be cancelled in current status'),
        404: OpenApiResponse(description='Order not found'),
    }
)
class OrderCancelView(APIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        order_number = kwargs.get('order_number')
        
        try:
            order = Order.objects.get(
                order_number=order_number,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            OrderService.cancel_order(order, request.user)
            return Response(
                {'message': 'Order cancelled successfully.'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )