from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from django.db import models 
from django.db.models import Q
from apps.products.models.warehouse_movement import WarehouseMovement
from apps.products.serializers.warehouse_movement import (
    WarehouseMovementSerializer,
    WarehouseMovementListSerializer
)
from apps.products.permissions import IsWarehouseManagerOrAdmin


@extend_schema_view(
    get=extend_schema(
        tags=['Warehouse Movement'],
        summary='List movements',
        description='Get all stock movements with filtering.',
        parameters=[
            OpenApiParameter(name='warehouse', type=int, description='Filter by warehouse ID'),
            OpenApiParameter(name='product', type=int, description='Filter by product ID'),
            OpenApiParameter(name='type', type=str, description='Filter by movement type'),
        ]
    )
)
class WarehouseMovementListView(generics.ListAPIView):
    serializer_class = WarehouseMovementListSerializer
    permission_classes = [IsWarehouseManagerOrAdmin]
    
    def get_queryset(self):
        qs = WarehouseMovement.objects.all().select_related(
            'product', 'source_warehouse', 'destination_warehouse', 'created_by'
        )
        
        warehouse = self.request.query_params.get('warehouse')
        if warehouse:
            qs = qs.filter(
                models.Q(source_warehouse_id=warehouse) |
                models.Q(destination_warehouse_id=warehouse)
            )
        
        product = self.request.query_params.get('product')
        if product:
            qs = qs.filter(product_id=product)
        
        movement_type = self.request.query_params.get('type')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        
        return qs


@extend_schema_view(
    get=extend_schema(
        tags=['Warehouse Movement'],
        summary='Get movement details',
    )
)
class WarehouseMovementDetailView(generics.RetrieveAPIView):
    queryset = WarehouseMovement.objects.all()
    serializer_class = WarehouseMovementSerializer
    permission_classes = [IsWarehouseManagerOrAdmin]
    lookup_field = 'pk'