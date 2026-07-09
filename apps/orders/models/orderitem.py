from django.db import models
from apps.accounts.models.user import CustomUser
from apps.products.models.product import Product
from apps.orders.models.order import Order

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='sold_items')
    # Snapshot of product data at time of order
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    fulfillment_warehouse = models.ForeignKey('warehouses.Warehouse',on_delete=models.SET_NULL,null=True,blank=True, related_name='fulfilled_order_items',help_text='Warehouse that stock was deducted from for this item') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        return self.product_price * self.quantity
    
    def save(self, *args, **kwargs):
        if not self.product:
            self.product_name = "Unknown Product"
            self.product_price = 0.00
        else:
            self.product_name = self.product.name
            self.product_price = self.product.price
        self.subtotal = self.total_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity} x {product_name} in Order {self.order.order_number}" 