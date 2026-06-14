from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    
    delivery_address = serializers.CharField(
        max_length=255,
        help_text='Street address for delivery'
    )
    delivery_city = serializers.CharField(
        max_length=100,
        help_text='City for delivery'
    )
    delivery_phone = serializers.CharField(
        max_length=20,
        help_text='Contact phone number'
    )
    notes = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text='Optional delivery instructions'
    )
    
    def validate_delivery_phone(self, value):

        if not value.strip():
            raise serializers.ValidationError('Phone number is required.')
        # Remove common formatting characters
        cleaned = value.replace('-', '').replace(' ', '').replace('+', '')
        if not cleaned.isdigit():
            raise serializers.ValidationError('Phone number contains invalid characters.')
        if len(cleaned) < 7:
            raise serializers.ValidationError('Phone number is too short.')
        return value