from rest_framework import serializers
from apps.carts.models.cart import Cart
from apps.carts.serializers.cartitem import CartItemSerializer

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
    