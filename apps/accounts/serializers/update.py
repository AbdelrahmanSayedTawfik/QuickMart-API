from rest_framework import serializers
from apps.accounts.models.user import CustomUser

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone']
        