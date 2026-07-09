from rest_framework import serializers
from apps.products.serializers.product import ProductSerializer
from apps.carts.models.cartitem import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = ProductSerializer(source='product', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity', 'product_name', 'product_id', 'total_price']
        read_only_fields = ['id', 'cart', 'product_name', 'product_id', 'total_price']

        