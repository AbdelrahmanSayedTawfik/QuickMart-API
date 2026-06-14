from django.db import models


class StockMovement(models.Model):
    # What kind of movement happened?
    MOVEMENT_TYPES = (
        ('in', 'Stock In'),           
        ('out', 'Stock Out'),         
        ('adjustment', 'Adjustment'), 
        ('return', 'Return'),         
    )
    
    # Link to the product that changed
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text='The product whose stock changed'
    )
    
    # What type of movement?
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        help_text='Why did stock change?'
    )
    
    # How many units moved?
    quantity = models.PositiveIntegerField(
        help_text='Number of units that moved'
    )
    
    
    # These are CRITICAL for audit. We snapshot the stock level.
    previous_stock = models.PositiveIntegerField(
        help_text='Stock level BEFORE this movement'
    )
    new_stock = models.PositiveIntegerField(
        help_text='Stock level AFTER this movement'
    )
    
    # ── WHY DID THIS HAPPEN? ──
    reason = models.CharField(
        max_length=255,
        help_text='Human-readable reason: "Order #123", "Monthly count", "Damaged"'
    )
    
    # Link to the order that caused this (optional)
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements',
        help_text='The order that caused this movement (if any)'
    )
    
    # ── WHO DID IT? ──
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements',
        help_text='User who initiated this movement'
    )
    
    # ── WHEN? ──
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest first
        indexes = [
            models.Index(fields=['product', '-created_at']),      # Fast product history lookup
            models.Index(fields=['movement_type', '-created_at']), # Fast filtering by type
            models.Index(fields=['created_by', '-created_at']),    # Fast "what did user X do?"
            models.Index(fields=['created_at']),                   # Fast date range queries
        ]
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
    
    @property
    def stock_change(self):
        if self.movement_type in ('in', 'return'):
            return f"+{self.quantity}"
        elif self.movement_type == 'out':
            return f"-{self.quantity}"
        else:
            change = self.new_stock - self.previous_stock
            sign = '+' if change > 0 else ''
            return f"{sign}{change}"
    
    def __str__(self):
        return (
            f'{self.product.name}: {self.previous_stock} → {self.new_stock} '
            f'({self.movement_type}) at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
        )