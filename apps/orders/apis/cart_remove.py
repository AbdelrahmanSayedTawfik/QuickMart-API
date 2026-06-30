from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.orders.services.cart import CartService


@extend_schema_view(
    delete=extend_schema(
        tags=['Cart'],
        summary='Remove item from cart',
        description='Removes a specific product from the user\'s cart.',
        request=None,
        responses={
            204: OpenApiResponse(description='Item removed successfully'),
            400: OpenApiResponse(description='Product ID required'),
            404: OpenApiResponse(description='Cart item not found'),
        }
    )
)
class CartRemoveItemView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        product_id = request.query_params.get('product') or request.data.get('product')
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            CartService.remove_item(
                user=request.user,
                product_id=int(product_id)
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )