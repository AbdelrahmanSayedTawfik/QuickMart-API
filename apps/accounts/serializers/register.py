from rest_framework import serializers
from apps.accounts.models.user import CustomUser
from apps.accounts.validators.password import PasswordValidator

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[PasswordValidator.validate])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'phone', 'address', 'role', 'avatar']
        read_only_fields = ['id', 'role'] 

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
    
    def create(self, validated_data):

        validated_data.pop('password2')

        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user


