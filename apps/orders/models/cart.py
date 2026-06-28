from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models.user import CustomUser
from apps.products.models.product import Product
from apps.orders.queryset.carts import CartQuerySet
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CartQuerySet.as_manager()
    @property
    def total(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def items_count(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    



