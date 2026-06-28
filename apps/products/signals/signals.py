# apps/products/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.products.models.category import Category
from apps.products.models.product import Product
from apps.products.services.cache import ProductCacheService


@receiver(post_save, sender=Product)
def invalidate_product_cache_on_save(sender, instance, **kwargs):
    ProductCacheService.invalidate_product_detail(instance.slug)
    ProductCacheService.invalidate_product_list_all()


@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    ProductCacheService.invalidate_product_detail(instance.slug)
    ProductCacheService.invalidate_product_list_all()


@receiver(post_save, sender=Category)
def invalidate_category_cache_on_save(sender, instance, **kwargs):
    ProductCacheService.invalidate_category_list()
    # Products are filtered by category so their cache is stale too
    ProductCacheService.invalidate_product_list_all()


@receiver(post_delete, sender=Category)
def invalidate_category_cache_on_delete(sender, instance, **kwargs):
    ProductCacheService.invalidate_category_list()
    ProductCacheService.invalidate_product_list_all()