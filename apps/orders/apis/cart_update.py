from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.orders.serializers.cart import CartItemSerializer
from apps.orders.services.cart import CartService


@extend_schema_view(
    put=extend_schema(
        tags=['Cart'],
        summary='Update item quantity',
        description='Updates the quantity of a specific product in the cart. Set to 0 to remove.',
        request=CartItemSerializer,
        responses={
            200: OpenApiResponse(
                response=CartItemSerializer,
                description='Quantity updated'
            ),
            400: OpenApiResponse(description='Invalid product or quantity'),
            404: OpenApiResponse(description='Cart item not found'),
        }
    )
)
class CartUpdateItemView(generics.UpdateAPIView):
    http_method_names = ['put']
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if not product_id or quantity is None:
            return Response(
                {'error': 'Product ID and quantity are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CartService.update_quantity(
                user=request.user,
                product_id=int(product_id),
                quantity=int(quantity)
            )
            
            if item is None:
                return Response(
                    {'message': 'Item removed from cart.'},
                    status=status.HTTP_200_OK
                )
            
            return Response(
                CartItemSerializer(item).data,
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )