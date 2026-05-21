from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product, ProductImage, Review
from django.core.cache import cache


@receiver(post_save, sender=Product)
def invalidate_product_cache_on_save(sender, instance, **kwargs):
    cache.delete('product_list_all')
    cache.delete(f'product_detail_{instance.slug}')
    delete_product_list_cache()
    

@receiver(post_delete, sender=Product)
def invalidate_product_cache_on_delete(sender, instance, **kwargs):
    cache.delete('product_list_all')
    cache.delete(f'product_detail_{instance.slug}')
    delete_product_list_cache()

def delete_product_list_cache():
    try:
        cache.delete_pattern('product_list_*')
    except AttributeError:
        # If delete_pattern is not available, we can manually track keys or skip this step
        pass    
    

@receiver(post_save, sender=Category)
def invalidate_category_cache_on_save(sender, instance, **kwargs):
    cache.delete('category_list')
    delete_product_list_cache()
    
@receiver(post_delete, sender=Category)
def invalidate_category_cache_on_delete(sender, instance, **kwargs):
    cache.delete('category_list')
    delete_product_list_cache()    