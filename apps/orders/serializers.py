from .models import Cart, CartItem, Order, OrderItem, OrderStatusLog
from rest_framework import serializers
from apps.products.serializers import ProductSerializer

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
    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = ProductSerializer(source='product', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'product_name', 'product_id', 'total_price']
        read_only_fields = ['id', 'order', 'product_name', 'product_id', 'total_price']   
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'status', 'created_at', 'items', 'total']
        read_only_fields = ['id', 'order_number', 'user', 'created_at', 'items', 'total']        
        
class OrderStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusLog
        fields = ['id', 'order', 'previous_status', 'new_status', 'changed_at']
        read_only_fields = ['id', 'order', 'previous_status', 'new_status', 'changed_at']
        
class CheckoutSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(max_length=255)
    delivery_city = serializers.CharField(max_length=100)
    delivery_phone = serializers.CharField(max_length=20)
    notes = serializers.CharField(allow_blank=True, required=False)
