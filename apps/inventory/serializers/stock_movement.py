from rest_framework import serializers
from apps.inventory.models.stock_movement import StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    # FIX: Added allow_null=True, default='' to prevent crashes on null relations
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True, default='')
    product_sku = serializers.CharField(source='product.sku', read_only=True, allow_null=True, default='')
    username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True, default='')
    order_number = serializers.CharField(source='order.order_number', read_only=True, allow_null=True, default='')
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
    # FIX: Added allow_null=True, default=''
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True, default='')

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product_name', 'movement_type',
            'quantity', 'new_stock', 'reason', 'created_at'
        ]