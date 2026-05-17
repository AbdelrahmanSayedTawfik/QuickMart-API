from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart, CartItem, Order, OrderItem

@receiver(post_save, sender=Order)
def update_stock_on_order_status_change(sender, instance, created, **kwargs):  
    if not created:
        # Check if status changed to 'paid'
        if instance.status == 'paid':
            for item in instance.items.select_related('product').all():
                product = item.product
                if product:
                    # Reduce stock quantity
                    product.stock_quantity -= item.quantity
                    # Update product status
                    if product.stock_quantity <= 0:
                        product.status = 'out_of_stock'
                    product.save()