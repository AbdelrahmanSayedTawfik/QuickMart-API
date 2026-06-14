from rest_framework import serializers
from apps.products.models.review import Review
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'is_verified_purchaser', 'created_at']
        read_only_fields = ['id','user', 'is_verified_purchaser', 'created_at']    
        
        
        def validate_purchasing(self, value):
            user = self.context['request'].user
            product = self.context['product']
            from apps.orders.models.orderitem import OrderItem
            has_purchased = OrderItem.objects.filter(order__user=user, product=product).exists()
            if not has_purchased:
                raise serializers.ValidationError("You can only review products you have purchased.")
            return value