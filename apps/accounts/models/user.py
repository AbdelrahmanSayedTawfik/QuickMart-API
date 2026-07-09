from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.accounts.querysets.users import CustomUserQuerySet
# Create your models here.

class CustomUser(AbstractUser):
    
    ROLES =[ ('customer', 'Customer'),
            ('seller', 'Seller'),
            ('admin', 'Admin'),
            ('warehouse_manager', 'Warehouse Manager'),
            ]
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True) 
    city = models.CharField(max_length=50, blank=True, null=True, help_text='City for shipping eligibility check')
    role = models.CharField(max_length=20, choices=ROLES, default='customer')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_seller = models.BooleanField(default=False)
    managed_warehouses = models.ManyToManyField('products.Warehouse',blank=True,related_name='managers',help_text='Warehouses this manager can access')
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.username
    
    def is_manager(self):
        return self.role == 'warehouse_manager'
    
    def manages(self, warehouse_id):
        if self.role == 'admin':
            return True
        return self.managed_warehouses.filter(id=warehouse_id).exists()
    
    
        
    
