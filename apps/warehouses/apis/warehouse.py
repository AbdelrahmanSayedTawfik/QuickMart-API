from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.warehouses.models.warehouse import Warehouse
from apps.warehouses.serializers.warehouse import WarehouseSerializer,WarehouseListSerializer
from apps.warehouses.permissions import IsWarehouseManagerOrAdmin

@extend_schema_view(
    get=extend_schema(
        tags=['Warehouse'],
        summary='List warehouses',
        description='Get all warehouses.'
    ),
    post=extend_schema(
        tags=['Warehouse'],
        summary='Create warehouse',
        description='Admin only. Create a new warehouse location.'
    )
)
class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    permission_classes = [IsWarehouseManagerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WarehouseListSerializer
        return WarehouseSerializer


@extend_schema_view(
    get=extend_schema(tags=['Warehouse'], summary='Get warehouse'),
    put=extend_schema(tags=['Warehouse'], summary='Update warehouse'),
    patch=extend_schema(tags=['Warehouse'], summary='Partial update'),
    delete=extend_schema(tags=['Warehouse'], summary='Delete warehouse'),
)
class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsWarehouseManagerOrAdmin]
    lookup_field = 'pk'