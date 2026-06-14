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
        Converts the user's cart into an order.
        
        **What happens:**
        1. Validates cart has items
        2. Validates stock availability for all items
        3. Creates order with snapshot prices
        4. Deducts inventory (with audit trail)
        5. Clears cart
        6. Sends confirmation email + WebSocket notification
        
        **All steps are atomic** — if anything fails, nothing is saved.
        ''',
        request=CheckoutSerializer,
        responses={
            201: OpenApiResponse(
                response=OrderSerializer,
                description='Order created successfully'
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
        # Step 1: Validate request data
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Step 2: Process checkout (ALL logic is in the service!)
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
        
        # Step 3: Send notifications (non-blocking)
        NotificationService.notify_order_created(order)
        
        # Step 4: Return created order
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )