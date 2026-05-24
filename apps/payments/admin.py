from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Payment monitoring.
    REMOVED: failure_reason (doesn't exist on Payment model)
    """
    
    list_display = [
        'order',
        'order_number',
        'amount',
        'currency',
        'status',
        'stripe_payment_intent_id',
        'paid_at',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'currency',
        'created_at',
        'paid_at'
    ]
    
    search_fields = [
        'order__order_number',
        'stripe_payment_intent_id',
        'stripe_charge_id'
    ]
    
    readonly_fields = [
        'order',
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'amount',
        'currency',
        'paid_at',
        'created_at'
        
    ]
    
    list_editable = ['status']

    def order_number(self, obj):
        return obj.order.order_number if obj.order else '-'
    order_number.short_description = 'Order #'