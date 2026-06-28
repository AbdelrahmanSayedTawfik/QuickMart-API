from apps.products.models.product import Product
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample

from apps.orders.serializers.cart import CartItemSerializer
from apps.orders.services.cart import CartService



@extend_schema_view(
    post=extend_schema(
        tags=['Cart'],
        summary='Add item to cart',
        description='''
        Adds a product to the user's cart.
        
        - Creates cart if none exists
        - Increments quantity if product already in cart
        - Validates stock availability
        ''',
        request=CartItemSerializer,
        responses={
            201: OpenApiResponse(
                response=CartItemSerializer,
                description='Item added or quantity updated'
            ),
            400: OpenApiResponse(description='Invalid product or quantity'),
            404: OpenApiResponse(description='Product not found'),
        },
        examples=[
            OpenApiExample(
                'Valid Request',
                value={'product': 1, 'quantity': 2},
                request_only=True,
            ),
        ]
    )
)
class CartAddItemView(generics.CreateAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CartService.add_item(
                user=request.user,
                product_id=int(product_id),
                quantity=quantity
            )
            return Response(
                CartItemSerializer(item).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )