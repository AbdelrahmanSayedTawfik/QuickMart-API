from rest_framework import serializers
from apps.warehouses.models.warehouse_movement import WarehouseMovement


class WarehouseMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    source_name = serializers.CharField(source='source_warehouse.name', read_only=True, default='External')
    destination_name = serializers.CharField(source='destination_warehouse.name', read_only=True, default='External')
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='System')
    
    class Meta:
        model = WarehouseMovement
        fields = [
            'id',
            'product_name',
            'movement_type',
            'quantity',
            'source_name',
            'destination_name',
            'source_stock_before',
            'destination_stock_before',
            'reference_id',
            'notes',
            'created_by_name',
            'created_at'
        ]
        read_only_fields = ['created_at']


class WarehouseMovementListSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = WarehouseMovement
        fields = [
            'id',
            'product_name',
            'movement_type',
            'quantity',
            'created_at'
        ]