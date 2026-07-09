from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'email',
        'role',
        'managed_warehouses_list',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'date_joined',
        'last_login'
    ]

    list_editable = ['role']

    list_filter = [
        'role',
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

    filter_horizontal = ['managed_warehouses']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('QuickMart Profile', {
            'fields': ('phone', 'address', 'city', 'role', 'avatar', 'is_seller', 'managed_warehouses')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('QuickMart Profile', {
            'fields': ('phone', 'address', 'city', 'role', 'avatar', 'is_seller', 'managed_warehouses')
        }),
    )

    readonly_fields = ['date_joined', 'last_login']

    def managed_warehouses_list(self, obj):
        return ", ".join(w.code for w in obj.managed_warehouses.all())
    managed_warehouses_list.short_description = 'Manages'