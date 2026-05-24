from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


# ─────────────────────────────────────────────
# CUSTOM USER ADMIN
# ─────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Extended user admin with e-commerce specific fields.
    Inherits from Django's built-in UserAdmin for password handling.
    """
    
 # ── LIST VIEW ──
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
        'last_login'
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'date_joined'
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name'
    ]
    

    
    # ── FORM FIELDS ──
    fieldsets = BaseUserAdmin.fieldsets 
    # ── ADD USER FORM ──
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('E-Commerce Profile', {
            'fields': ('phone_number', 'is_seller')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


