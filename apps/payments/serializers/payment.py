from rest_framework import serializers
from apps.payments.models.payment import Payment


class PaymentSerializer(serializers.ModelSerializer):

    
    order_number = serializers.CharField(
        source='order.order_number',
        read_only=True
    )
    is_paid = serializers.ReadOnlyField()
    amount_in_cents = serializers.ReadOnlyField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number',
            'stripe_payment_intent_id', 'stripe_charge_id',
            'amount', 'amount_in_cents', 'currency',
            'status', 'failure_reason', 'is_paid',
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'amount', 'currency', 'paid_at', 'created_at', 'updated_at'
        ]


class PaymentIntentResponseSerializer(serializers.Serializer):

    
    client_secret = serializers.CharField(
        help_text='Stripe client_secret for frontend Stripe.js'
    )
    publishable_key = serializers.CharField(
        help_text='Your Stripe publishable key'
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Amount to be charged'
    )
    order_number = serializers.CharField(
        help_text='Order identifier'
    )


class PaymentStatusSerializer(serializers.Serializer):

    
    order_number = serializers.CharField()
    order_status = serializers.CharField()
    payment_status = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    currency = serializers.CharField(required=False)
    paid_at = serializers.DateTimeField(required=False)
    stripe_payment_intent_id = serializers.CharField(required=False)