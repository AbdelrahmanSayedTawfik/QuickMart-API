from apps.products.services.product import ProductService
from rest_framework import serializers
from apps.products.models.product import Product


class ProductListSerializer(serializers.ModelSerializer):

    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'original_price',
            'discount_percentage', 'stock_status', 'is_on_stock',
            'seller_name'
        ]
        read_only_fields = ['seller_name']



# ── FULL product serializer (for detail view) ──
class ProductSerializer(serializers.ModelSerializer):

    discount_percentage = serializers.ReadOnlyField()
    is_on_stock = serializers.ReadOnlyField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'description',
            'original_price', 'price', 'discount_percentage',
            'stock_quantity', 'stock_status', 'is_on_stock',
            'status', 'is_active', 'is_featured',
            'seller', 'seller_name',
            'category', 'category_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'stock_status', 'created_at', 'updated_at', 'seller'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('stock_quantity', None)
        return data

    def update(self, instance, validated_data):
        validated_data.pop('seller', None)
        return ProductService.update_product(product=instance, data=validated_data)