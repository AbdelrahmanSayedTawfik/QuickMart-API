from django.db import models
from apps.inventory.querysets.stock_alerts import StockAlertQuerySet
from apps.products.models.product import Product
from apps.orders.models.order import Order
from apps.accounts.models.user import CustomUser
class StockAlert(models.Model):
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('back_in_stock', 'Back In Stock'),
    )
    
    # Which product has the problem?
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_alerts',
        help_text='Product that triggered this alert'
    )
    
    # What kind of alert?
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        help_text='Why was this alert created?'
    )
    
    # At what stock level was this triggered?
    stock_at_trigger = models.PositiveIntegerField(
        help_text='Stock quantity when alert was created'
    )
    
    # What is the threshold for this product?
    threshold = models.PositiveIntegerField(
        default=10,
        help_text='Alert when stock goes below this number'
    )
    
    objects = StockAlertQuerySet.as_manager()
    
    # ── ALERT STATUS ──
    is_resolved = models.BooleanField(
        default=False,
        help_text='Has someone addressed this alert?'
    )
    resolved_at = models.DateTimeField(
        null=True, blank=True,
        help_text='When was this alert resolved?'
    )
    resolved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_alerts',
        help_text='Who resolved this alert?'
    )
    resolution_note = models.TextField(
        blank=True, null=True,
        help_text='Notes about how this was resolved'
    )
    
    # ── NOTIFICATION TRACKING ──
    email_sent = models.BooleanField(
        default=False,
        help_text='Was an email notification sent?'
    )
    email_sent_at = models.DateTimeField(
        null=True, blank=True
    )
    
    # ── TIMESTAMPS ──
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['alert_type', 'is_resolved']),
            models.Index(fields=['is_resolved', '-created_at']),
        ]
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'
    
    def resolve(self, user, note=''):
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_note = note
        self.save()
    
    def __str__(self):
        status = '✅' if self.is_resolved else '🔴'
        return f'{status} {self.alert_type} for {self.product.name} (stock: {self.stock_at_trigger})'