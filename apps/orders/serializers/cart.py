from rest_framework import serializers
from apps.products.serializers.product import ProductSerializer
from apps.orders.models.cartitem import CartItem
from apps.orders.models.cart import Cart


class CartItemSerializer(serializers.ModelSerializer):
    product_name = ProductSerializer(source='product', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'product_name', 'product_id', 'total_price']
        read_only_fields = ['id', 'cart', 'product_name', 'product_id', 'total_price']

        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    items_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total', 'items_count']
        read_only_fields = ['id', 'user', 'created_at', 'items', 'total', 'items_count']
        
    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())     
    