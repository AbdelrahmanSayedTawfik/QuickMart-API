from django.db import models
from django.core.exceptions import ValidationError

from apps.accounts.models.user import CustomUser
from apps.orders.queryset.orders import OrderQuerySet
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.CharField(max_length=255)
    delivery_city = models.CharField(max_length=100)
    delivery_phone = models.CharField(max_length=20)
    objects = OrderQuerySet.as_manager()
    notes = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"QM-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"