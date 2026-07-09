from django.contrib import admin
from .models import Order, OrderItem


# ─────────────────────────────────────────────
# INLINE: Order Items inside Order
# ─────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product', 
        'product_name', 
        'product_price', 
        'quantity', 
        'seller'
    ]
    
    can_delete = False

    def subtotal_display(self, obj):
        """Calculate subtotal since field doesn't exist."""
        return obj.product_price * obj.quantity if obj.product_price else 0
    subtotal_display.short_description = 'Subtotal'


# ─────────────────────────────────────────────
# ORDER ADMIN
# ─────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'user',
        'status',
        'total',
        'item_count',
        'created_at',
        'paid_at'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'paid_at'
    ]
    
    search_fields = [
        'order_number',
        'user__username',
        'user__email',
        'delivery_phone'
    ]
    
    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'paid_at',
        'subtotal',
        'tax',
        'shipping_fee',
        'total'
    ]
    
    list_editable = ['status']
    
    # ── BULK ACTIONS ──
    actions = [
        'mark_pending',
        'mark_processing',
        'mark_shipped',
        'mark_delivered',
        'mark_cancelled'
    ]
    
    # ── FORM LAYOUT ──
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Financials', {
            'fields': ('subtotal', 'tax', 'shipping_fee', 'total'),
            'classes': ('collapse',)
        }),
        ('Delivery', {
            'fields': (
                'delivery_address', 
                'delivery_city', 
                'delivery_phone', 
                'notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    # ── PERFORMANCE ──
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    # ── CUSTOM COLUMNS ──
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    # ── BULK ACTIONS ──
    def mark_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f'{queryset.count()} orders marked as pending.')
    mark_pending.short_description = "⏳ Mark as Pending"

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f'{queryset.count()} orders marked as processing.')
    mark_processing.short_description = "🔧 Mark as Processing"

    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_shipped.short_description = "🚚 Mark as Shipped"

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_delivered.short_description = "✅ Mark as Delivered"

    def mark_cancelled(self, request, queryset):
        cancelled_count = 0
        for order in queryset:
            if order.status != 'cancelled':
                for item in order.items.all():
                    product = item.product
                    if product:
                        product.stock_quantity += item.quantity
                        if product.stock_quantity > 0 and product.status == 'out_of_stock':
                            product.status = 'available'
                        product.save()
                order.status = 'cancelled'
                order.save()
                cancelled_count += 1
        self.message_user(request, f'{cancelled_count} orders cancelled and stock restored.')
    mark_cancelled.short_description = "❌ Cancel orders & restore stock"


