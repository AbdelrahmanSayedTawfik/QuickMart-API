from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100,unique=True, help_text="Name of the warehouse")
    code = models.CharField(max_length=10, unique=True, help_text="Unique code for the warehouse")
    address = models.TextField(help_text="Address of the warehouse")
    city = models.CharField(max_length=100,blank=True,null=True,help_text='City this warehouse serves for shipping')
    is_active = models.BooleanField(default=True, help_text="Indicates whether the warehouse is active or not")
    is_default = models.BooleanField(default=False, help_text=" Default Warehouse for new stock and orders ")
    manager_name = models.CharField(max_length=50, blank=True, help_text="Person responsible for this warehouse")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name'] 
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        
    def __str__(self):
        return f'{self.name} ({self.code})'
    
    def save (self , *args, **kwargs):
        if self.is_default:
            Warehouse.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)    
            
