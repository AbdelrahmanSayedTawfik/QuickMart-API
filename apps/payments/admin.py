# apps/payments/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'amount', 'currency',
        'status', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'stripe_payment_intent_id',
        'order__order_number'
    ]
    readonly_fields = [
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'created_at',
        
    ]