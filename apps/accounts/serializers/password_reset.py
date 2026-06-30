from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    token        = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    refresh      = serializers.CharField(write_only=True, required=False) 


    def validate_new_password(self, value):
        validate_password(value)
        return value