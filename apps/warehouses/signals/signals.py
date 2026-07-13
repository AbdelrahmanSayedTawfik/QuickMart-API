from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.warehouses.models.warehouse_stock import WarehouseStock


@receiver([post_save, post_delete], sender=WarehouseStock)
def sync_product_stock(sender, instance, **kwargs):

    if instance.Product:
        instance.Product.refresh_stock_from_warehouses()