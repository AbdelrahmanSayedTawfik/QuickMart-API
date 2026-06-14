from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.orders.models.order import Order


@receiver(post_save, sender=Order)
def update_stock_on_order_paid(sender, instance, created, **kwargs):

    if not created and instance.status == 'paid':
        # Check if stock was already deducted during checkout
        # by looking for existing StockMovement records
        from apps.inventory.models.stock_movement import StockMovement
        
        existing = StockMovement.objects.filter(
            order=instance,
            movement_type='out'
        ).exists()
        
        if not existing:
            # Stock wasn't deducted during checkout — deduct now
            from apps.inventory.services.stock import InventoryService
            
            for item in instance.items.select_related('product'):
                if item.product:
                    InventoryService.deduct_stock(
                        product=item.product,
                        quantity=item.quantity,
                        reason=f'Order paid: {instance.order_number}',
                        order=instance
                    )