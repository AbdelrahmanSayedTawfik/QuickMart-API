from .models import Category, Product, ProductImage, Review
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id','slug', 'created_at', 'updated_at']
        
        
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
    
    
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'is_verified_purchaser', 'created_at']
        read_only_fields = ['id','user', 'is_verified_purchaser', 'created_at']    
        
        
        def validate_purchasing(self, value):
            user = self.context['request'].user
            product = self.context['product']
            has_purchased = OrderItem.objects.filter(order__user=user, product=product).exists()
            if not has_purchased:
                raise serializers.ValidationError("You can only review products you have purchased.")
            return value