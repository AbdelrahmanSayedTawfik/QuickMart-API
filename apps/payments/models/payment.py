from django.db import models
from apps.orders.models.order import Order
from apps.payments.querysets.payments import PaymentQuerySet
# Create your models here.

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('processing', 'Processing'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True  , null=True,blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    objects = PaymentQuerySet.as_manager()
    class Meta:
        ordering = ['-created_at']
    
    @property
    def is_paid(self):
        
        return self.status == 'succeeded'
    
    @property
    def amount_in_cents(self):
        
        return int(self.amount * 100)
    
    def mark_as_succeeded(self, charge_id: str = None):
        
        from django.utils import timezone
        self.status = 'succeeded'
        self.stripe_charge_id = charge_id or self.stripe_charge_id
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'stripe_charge_id', 'paid_at', 'updated_at'])
    
    def mark_as_failed(self, reason: str = None):
        
        self.status = 'failed'
        self.failure_reason = reason or self.failure_reason
        self.save(update_fields=['status', 'failure_reason', 'updated_at'])
    
    def __str__(self):
        return f"Payment {self.stripe_payment_intent_id} — {self.status} (${self.amount})"
