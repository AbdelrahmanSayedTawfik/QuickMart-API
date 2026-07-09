from rest_framework import serializers
from apps.products.serializers.warehouse import WarehouseListSerializer
from apps.products.models.warehouse_stock import WarehouseStock
from apps.products.models.product import Product
from apps.products.models.warehouse import Warehouse


class StockSerializer(serializers.ModelSerializer):
    warehouse = WarehouseListSerializer(read_only=True)
    product_name = serializers.CharField(source='Product.name', read_only=True)
    product_sku = serializers.CharField(source='Product.sku', read_only=True)

    class Meta:
        model = WarehouseStock
        fields = (
            'id', 'warehouse', 'product_name', 'product_sku',
            'quantity','low_stock_threshold', 'updated_at',
        )
        read_only_fields = ('updated_at', 'transfer_in', 'transfer_out')


class InOutSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    qty = serializers.IntegerField(min_value=1)
    ref = serializers.CharField(required=False, allow_blank=True, default='')
    note = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_product_id(self, val):
        if not Product.objects.filter(id=val).exists():
            raise serializers.ValidationError('Product not found.')
        return val


class TransferSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    qty = serializers.IntegerField(min_value=1)
    dest_wh_id = serializers.IntegerField(min_value=1)
    ref = serializers.CharField(required=False, allow_blank=True, default='')
    note = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_product_id(self, val):
        if not Product.objects.filter(id=val).exists():
            raise serializers.ValidationError('Product not found.')
        return val

    def validate_dest_wh_id(self, val):
        if not Warehouse.objects.filter(id=val, is_active=True).exists():
            raise serializers.ValidationError('Warehouse not found.')
        return val


class AdjustSerializer(serializers.Serializer):
    qty = serializers.IntegerField(min_value=0)
    reason = serializers.CharField(required=False, allow_blank=True, default='')


class ShipCheckSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    qty = serializers.IntegerField(min_value=1)
    city = serializers.CharField(required=False, allow_blank=True)