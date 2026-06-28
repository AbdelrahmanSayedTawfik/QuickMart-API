from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.orders.models.order import Order
from apps.orders.serializers.order import OrderSerializer



@extend_schema_view(
    get=extend_schema(
        tags=['Orders'],
        summary='List my orders',
        description='Returns all orders for the authenticated user, newest first.',
        responses={
            200: OpenApiResponse(
                response=OrderSerializer,
                description='List of user orders'
            ),
        }
    )
)
class OrderListView(generics.ListAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.for_user(self.request.user).with_items().recent()