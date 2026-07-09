from django.contrib import admin
from .models.cart import Cart
from .models.cartitem import CartItem
# Register your models here.
# ─────────────────────────────────────────────
# CART ADMIN
# ─────────────────────────────────────────────
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'created_at', 'updated_at']
    readonly_fields = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# ─────────────────────────────────────────────
# CART ITEM ADMIN
# ─────────────────────────────────────────────
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    REMOVED: subtotal from list_display (doesn't exist as field)
    Added custom method instead.
    """
    list_display = ['cart', 'product', 'quantity', 'subtotal_display']
    readonly_fields = ['cart', 'product', 'quantity']
    list_filter = ['product__category']

    def subtotal_display(self, obj):
        """Calculate subtotal: price × quantity"""
        if obj.product:
            return obj.product.price * obj.quantity
        return 0
    subtotal_display.short_description = 'Subtotal'