from django.contrib import admin
from .models import Product, Category, ProductImage, Review


# ─────────────────────────────────────────────
# INLINE: Product Images inside Product
# ─────────────────────────────────────────────
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image']  

# ─────────────────────────────────────────────
# INLINE: Reviews inside Product
# ─────────────────────────────────────────────
class ReviewInline(admin.TabularInline):
    """
    Shows reviews directly on the product page.
    Read-only so admins can't fake reviews.
    """
    model = Review
    extra = 0  # Don't show empty slots
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = True  # Allow removing bad reviews


# ─────────────────────────────────────────────
# CATEGORY ADMIN
# ─────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


# ─────────────────────────────────────────────
# PRODUCT ADMIN
# ─────────────────────────────────────────────
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product management.
    Only uses fields that exist on your actual Product model.
    """
    
    # ── LIST VIEW ──
    list_display = [
        'name', 
        'seller', 
        'category', 
        'price', 
        'stock_quantity', 
        'status', 
        'is_featured', 
        'created_at'
    ]
    
    
    list_filter = [
        'status', 
        'category', 
        'is_featured',  
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'sku', 
        'seller__username',
        'seller__email',
        'description'
    ]
    
    list_editable = [
        'status', 
        'is_featured'  
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at'
        
    ]
    
    # ── BULK ACTIONS ──
    actions = [
        'mark_featured',
        'mark_unfeatured',
        'mark_out_of_stock',
        'mark_available',
    ]
    
    # ── FORM LAYOUT ──
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'status'),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('category', 'seller', 'is_featured') 
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # ── INLINES ──
    inlines = [ProductImageInline, ReviewInline]  
    
    # ── PERFORMANCE ──
    list_select_related = ['seller', 'category']
    list_per_page = 25
    
    # ── BULK ACTIONS ──
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} product(s) marked as featured.')
    mark_featured.short_description = "⭐ Mark selected as featured"

    def mark_unfeatured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} product(s) removed from featured.')
    mark_unfeatured.short_description = "❌ Mark selected as unfeatured"

    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(status='out_of_stock')
        self.message_user(request, f'{updated} product(s) marked as out of stock.')
    mark_out_of_stock.short_description = "📦 Mark selected as out of stock"

    def mark_available(self, request, queryset):
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} product(s) marked as available.')
    mark_available.short_description = "✅ Mark selected as available"


# ─────────────────────────────────────────────
# REVIEW ADMIN (Simplified)
# ─────────────────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Manage customer reviews.
    REMOVED: is_approved (doesn't exist on your Review model)
    """
    list_display = [
        'product', 
        'user', 
        'rating', 
        'comment', 
        'created_at'
    ]
    
    
    list_filter = ['rating', 'created_at']
    search_fields = [
        'comment', 
        'user__username', 
        'product__name'
    ]
    readonly_fields = ['created_at']