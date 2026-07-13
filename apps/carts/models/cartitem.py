from django.db import models
from django.core.exceptions import ValidationError
from apps.carts.models.cart import Cart
from apps.products.models.product import Product

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders_cartitem' 
        unique_together = ('cart', 'product')
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def clean(self):
        if self.quantity < 1:
            raise ValidationError('Quantity must be at least 1.')

        from apps.warehouses.models.warehouse_stock import WarehouseStock

        city = getattr(self.cart.user, 'city', None)

        if city:
            stock = WarehouseStock.objects.filter(
                Product=self.product,
                Warehouse__city__iexact=city,
                Warehouse__is_active=True
            ).order_by('-quantity').first()
            available = stock.quantity if stock else 0
        else:
            
            total = WarehouseStock.objects.filter(
                Product=self.product,
                Warehouse__is_active=True
            ).aggregate(total=models.Sum('quantity'))['total'] or 0
            available = total  

        if self.quantity > available:
            location = city or 'any warehouse'
            raise ValidationError(
                f'Not enough stock for "{self.product.name}" in {location}. '
                f'Available: {available}, Requested: {self.quantity}'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"    
