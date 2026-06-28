from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample

from apps.orders.serializers.checkout import CheckoutSerializer
from apps.orders.serializers.order import OrderSerializer
from apps.orders.services.checkout import CheckoutService
from apps.orders.services.notification import NotificationService


@extend_schema_view(
    post=extend_schema(
        tags=['Orders'],
        summary='Place order from cart',
        description='''
        Converts the user's cart into a pending order.
        
        **What happens:**
        1. Validates cart has items
        2. Validates stock availability for all items (read-only check)
        3. Creates order with snapshot prices
        4. Clears cart
        5. Sends order created notification
        
        **Stock is NOT deducted here** — it is deducted when payment is confirmed.
        **All steps are atomic** — if anything fails, nothing is saved.
        ''',
        request=CheckoutSerializer,
        responses={
            201: OpenApiResponse(
                response=OrderSerializer,
                description='Order created successfully (pending payment)'
            ),
            400: OpenApiResponse(
                description='Cart empty, stock insufficient, or invalid address'
            ),
        },
        examples=[
            OpenApiExample(
                'Checkout Request',
                value={
                    'delivery_address': '123 Main St',
                    'delivery_city': 'New York',
                    'delivery_phone': '+1234567890',
                    'notes': 'Leave at door'
                },
                request_only=True,
            ),
        ]
    )
)
class CheckoutView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            order = CheckoutService.process(
                user=request.user,
                checkout_data=serializer.validated_data
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        NotificationService.notify_order_created(order)
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )