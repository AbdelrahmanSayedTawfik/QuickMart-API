from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models.user import CustomUser


@receiver(post_save, sender=CustomUser)
def create_cart_for_new_user(sender, instance, created, **kwargs):

    if created and instance.role == 'customer':
        # Import here to avoid circular imports
        from apps.carts.models.cart import Cart
        Cart.objects.create(user=instance)