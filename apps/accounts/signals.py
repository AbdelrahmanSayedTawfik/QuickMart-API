
# (auto-create cart when user registers):
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created and instance.role == 'customer':  # Only create cart for customers
        # Assuming you have a Cart model with a ForeignKey to CustomUser
        from .models import Cart
        Cart.objects.create(user=instance)
