from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.carts.models.cart import Cart
from apps.carts.serializers.cart import CartSerializer
from apps.carts.services.cart import CartService


@extend_schema_view(
    get=extend_schema(
        tags=['Cart'],
        summary='Get current cart',
        description='Returns the authenticated user\'s shopping cart with all items and calculated totals.',
        responses={
            200: OpenApiResponse(
                response=CartSerializer,
                description='Cart with items and calculated totals'
            ),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
)
class CartView(generics.RetrieveAPIView):

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart = CartService.get_or_create_cart(self.request.user)
        return cart