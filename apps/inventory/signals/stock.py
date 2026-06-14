from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.products.models.product import Product
from apps.inventory.services.alert import AlertService


@receiver(post_save, sender=Product)
def check_stock_alerts(sender, instance, created, **kwargs):


    if not created:
        AlertService.check_and_create_alerts(instance)