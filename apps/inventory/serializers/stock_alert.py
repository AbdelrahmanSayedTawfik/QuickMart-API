from rest_framework import serializers
from apps.inventory.models.stock_alert import StockAlert


class StockAlertSerializer(serializers.ModelSerializer):

    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    current_stock = serializers.IntegerField(source='product.stock_quantity', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'alert_type', 'stock_at_trigger', 'current_stock', 'threshold',
            'is_resolved', 'resolved_at', 'resolved_by', 'resolved_by_name',
            'resolution_note', 'email_sent', 'created_at'
        ]
        read_only_fields = [
            'id', 'stock_at_trigger', 'created_at',
            'email_sent', 'email_sent_at'
        ]


class ResolveAlertSerializer(serializers.Serializer):

    resolution_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text='Notes about how this was resolved'
    )