from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
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
    
    # Keep default fieldsets (no extra fields)
    fieldsets = BaseUserAdmin.fieldsets
    
    # Keep default add_fieldsets (no extra fields)
    add_fieldsets = BaseUserAdmin.add_fieldsets
    
    readonly_fields = ['date_joined', 'last_login']