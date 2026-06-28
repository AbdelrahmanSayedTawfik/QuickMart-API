from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.accounts.querysets.users import CustomUserQuerySet
# Create your models here.

class CustomUser(AbstractUser):
    
    ROLES =[ ('customer', 'Customer'),
            ('seller', 'Seller'),
            ('admin', 'Admin')]
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True) 
    role = models.CharField(max_length=20, choices=ROLES, default='customer')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_seller = models.BooleanField(default=False)
    #objects = CustomUserQuerySet.as_manager()    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.username
    
    
        
    
