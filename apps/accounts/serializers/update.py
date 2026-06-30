from rest_framework import serializers
from apps.accounts.models.user import CustomUser


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone', 'address',
            'first_name', 'last_name', 'avatar'
        ]
        read_only_fields = ['id', 'username', 'email']  
    
    def validate_phone(self, value):
        
        if value and not value.startswith('+'):
            raise serializers.ValidationError('Phone must start with +')
        return value