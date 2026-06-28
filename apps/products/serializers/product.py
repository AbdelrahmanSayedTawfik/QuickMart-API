from apps.products.services.product import ProductService
from rest_framework import serializers
from apps.products.models.product import Product,ProductImage



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_main']



class ProductListSerializer(serializers.ModelSerializer):

    primary_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'original_price',
            'discount_percentage', 'stock_status', 'is_on_stock',
            'seller_name', 'primary_image'
        ]
        read_only_fields = ['seller_name']
    
    def get_primary_image(self, obj):
        
        primary = obj.images.filter(is_main=True).first()
        if primary:
            return self.context['request'].build_absolute_uri(primary.image.url)
        return None


# ── FULL product serializer (for detail view) ──
class ProductSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(many=True, read_only=True)
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
            'category', 'category_name', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'stock_status','created_at', 'updated_at'
        ]
        
    def update(self, instance, validated_data):
        validated_data.pop('seller', None)
        return ProductService.update_product(product=instance, data=validated_data)    