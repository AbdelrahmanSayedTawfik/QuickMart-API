from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.carts.services.cart import CartService


@extend_schema_view(
    delete=extend_schema(
        tags=['Cart'],
        summary='Clear entire cart',
        description='Removes ALL items from the user\'s cart. Cart object is preserved.',
        responses={
            204: OpenApiResponse(description='Cart cleared successfully'),
        }
    )
)
class CartClearItemsView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        CartService.clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)