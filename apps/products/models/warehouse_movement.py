from django.db import models

from apps.products.models.product import Product
from apps.accounts.models.user import CustomUser
from apps.products.models.warehouse import Warehouse


class WarehouseMovement(models.Model):

    MOVEMENT_TYPES = (
        ('in', 'Stock In'),              
        ('out', 'Stock Out'),            
        ('transfer_in', 'Transfer In'),  
        ('transfer_out', 'Transfer Out'), 
        ('adjustment', 'Adjustment'),   
    )
    

    source_warehouse = models.ForeignKey("products.Warehouse",on_delete=models.SET_NULL,null=True,blank=True,related_name='outgoing_movements', help_text='Warehouse stock LEFT from. NULL for supplier.')
    destination_warehouse = models.ForeignKey(Warehouse,on_delete=models.SET_NULL,null=True,blank=True,related_name='incoming_movements',help_text='Warehouse stock ARRIVED at. NULL for customer.')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='warehouse_movements', help_text='Which product moved')
    movement_type = models.CharField(max_length=20,choices=MOVEMENT_TYPES,help_text='Why did this movement happen')
    quantity = models.PositiveIntegerField(help_text='How many units moved')
    source_stock_before = models.PositiveIntegerField(null=True,blank=True,help_text='Stock at source warehouse BEFORE this movement')
    destination_stock_before = models.PositiveIntegerField(null=True,blank=True,help_text='Stock at destination warehouse BEFORE this movement')
    source_after = models.PositiveIntegerField(null=True,blank=True,help_text='Source warehouse stock AFTER this move')
    dest_after = models.PositiveIntegerField(null=True,blank=True,help_text='Destination warehouse stock AFTER this move')
    reference_id = models.CharField(max_length=100,blank=True,help_text='Order number, transfer ID, or adjustment reference')
    notes = models.TextField(blank=True,help_text='Human-readable reason')
    created_by = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name='warehouse_movements',help_text='User who initiated this movement')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['source_warehouse', '-created_at']),
            models.Index(fields=['destination_warehouse', '-created_at']),
            models.Index(fields=['movement_type', '-created_at']),
        ]
        
        verbose_name = 'Warehouse Movement'
        verbose_name_plural = 'Warehouse Movements'
    
    def __str__(self):
        direction = '→'
        if self.source_warehouse and self.destination_warehouse:
            direction = f'{self.source_warehouse.code} → {self.destination_warehouse.code}'
        elif self.source_warehouse:
            direction = f'{self.source_warehouse.code} → EXTERNAL'
        elif self.destination_warehouse:
            direction = f'EXTERNAL → {self.destination_warehouse.code}'
        
        return f'{self.product.name} {direction} ({self.quantity}) [{self.movement_type}]'