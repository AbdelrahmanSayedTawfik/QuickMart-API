from rest_framework import serializers
from apps.products.models.category import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id','slug', 'created_at', 'updated_at']
        