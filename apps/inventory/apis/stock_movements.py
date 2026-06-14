from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter

from apps.inventory.models.stock_movement import StockMovement
from apps.inventory.serializers.stock_movement import StockMovementSerializer, StockMovementListSerializer
from apps.products.permissions import IsAdminOrReadOnly


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory'],
        summary='List stock movements',
        description='''
        Get stock movement history with filtering.
        
        **Query Parameters:**
        - `product` — Filter by product ID
        - `movement_type` — Filter by type (in, out, adjustment, return)
        - `days` — Only last N days
        ''',
        parameters=[
            OpenApiParameter(name='product', type=int, description='Product ID'),
            OpenApiParameter(name='movement_type', type=str, description='in | out | adjustment | return'),
            OpenApiParameter(name='days', type=int, description='Last N days'),
        ],
    )
)
class StockMovementListView(generics.ListAPIView):

    serializer_class = StockMovementListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        qs = StockMovement.objects.with_product_details()
        
        # Filter by product
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.for_product(product_id)
        
        # Filter by type
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            qs = qs.by_type(movement_type)
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            qs = qs.recent(days=int(days))
        
        # Non-admins only see their own products' movements
        if self.request.user.role != 'admin':
            qs = qs.filter(product__seller=self.request.user)
        
        return qs


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory'],
        summary='Get stock movement details',
    )
)
class StockMovementDetailView(generics.RetrieveAPIView):

    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]