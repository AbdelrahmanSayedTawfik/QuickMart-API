from rest_framework import serializers
from apps.inventory.models.stock_movement import StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    username = serializers.CharField(source='created_by.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    stock_change = serializers.ReadOnlyField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'movement_type', 'quantity', 'stock_change',
            'previous_stock', 'new_stock',
            'reason', 'order', 'order_number',
            'created_by', 'username',
            'created_at'
        ]
        read_only_fields = [
            'id', 'previous_stock', 'new_stock',
            'created_at', 'stock_change'
        ]


class StockMovementListSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product_name', 'movement_type',
            'quantity', 'new_stock', 'reason', 'created_at'
        ]