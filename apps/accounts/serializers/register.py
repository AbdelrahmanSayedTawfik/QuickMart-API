from rest_framework import serializers
from apps.accounts.models.user import CustomUser
from apps.accounts.validators.password import PasswordValidator
from apps.warehouses.services.city_service import WarehouseCityService
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[PasswordValidator.validate])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'phone','city', 'address', 'avatar']
        read_only_fields = ['id'] 

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_email(self, value):
    # ADD THIS METHOD — checks email uniqueness
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value
    
    def validate_city(self, value):
        if not value:
            raise serializers.ValidationError('City Is Required')
        available = WarehouseCityService.get_available_cities()
        if value not in available:
            raise serializers.ValidationError(
                f'We don\'t currently deliver to "{value}".'
            )
        return value
    
    def create(self, validated_data):

        validated_data.pop('password2')

        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user
    
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['role'] = instance.role
        return data


