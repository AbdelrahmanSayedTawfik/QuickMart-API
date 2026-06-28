from rest_framework import serializers
from apps.products.serializers.product import ProductSerializer
from apps.orders.models.order import Order
from apps.orders.models.orderitem import OrderItem

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