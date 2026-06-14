from rest_framework import serializers
from apps.products.models.product import Product,ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'created_at']
        read_only_fields = ['id','created_at']     

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    is_on_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'description', 'price', 'original_price', 'stock_quantity', 'is_featured', 'status', 'slug', 'sku', 'view_count', 'created_at', 'updated_at', 'discount_percentage', 'is_on_stock', 'average_rating', 'images','seller']
        read_only_fields = ['id','slug', 'view_count','created_at', 'updated_at','seller']
    
    

