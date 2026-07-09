from django.db import models,transaction
from django.core.validators import MinValueValidator

from apps.products.models.product import Product
from apps.products.models.warehouse import Warehouse


class WarehouseStock(models.Model):
    Warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='warehouse_stocks')
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warehouse_stocks')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0, help_text="Quantity of the product in the warehouse")
    low_stock_threshold = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=5, help_text="Threshold for low stock alert")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('Warehouse', 'Product')
        ordering = ['Warehouse', 'Product']
        indexes = [
            models.Index(fields=['Warehouse', 'quantity']),
            models.Index(fields=['Warehouse','Product']),
        ]
        verbose_name = 'Warehouse Stock'
        verbose_name_plural = 'Warehouse Stocks'
        
    def __str__(self):
        return f'{self.Product.name} in {self.Warehouse.name} - Quantity: {self.quantity}'
        
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
        
    def is_out_of_stock(self):
        return self.quantity == 0
        
    