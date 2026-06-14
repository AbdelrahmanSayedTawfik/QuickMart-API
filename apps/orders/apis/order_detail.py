from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter

from apps.orders.models.order import Order
from apps.orders.serializers.order import OrderSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Orders'],
        summary='Get order details',
        description='Retrieves full details of a specific order by order number.',
        parameters=[
            OpenApiParameter(
                name='order_number',
                type=str,
                location=OpenApiParameter.PATH,
                description='Unique order identifier (e.g., QM-ABC123DEF456)'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OrderSerializer,
                description='Order details with items'
            ),
            404: OpenApiResponse(description='Order not found'),
        }
    )
)
class OrderDetailView(generics.RetrieveAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        return Order.objects.for_user(self.request.user).with_items()