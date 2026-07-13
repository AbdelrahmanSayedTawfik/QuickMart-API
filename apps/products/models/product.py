from django.db import models
from apps.accounts.models.user import CustomUser
from apps.products.models.category import Category
from apps.products.querysets.products import ProductQuerySet

class Product(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('discontinued', 'Discontinued'),
    )
    STOCK_STATUS_CHOICES = (
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-order'),
    )
    
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    objects = ProductQuerySet.as_manager()
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    slug = models.SlugField(max_length=100, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='out_of_stock')
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['seller', 'status']),
        ]
    
    @property
    def discount_percentage(self):
        if self.original_price > 0:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return round(discount, 2)
        return 0.00
    
    @property
    def is_on_stock(self):
        return self.stock_quantity > 0 and self.status == 'available'
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_verified_purchaser=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return None

    def update_stock_status(self):
        if self.stock_quantity <= 0:
            self.stock_status = 'out_of_stock'
        elif self.stock_quantity < 10:
            self.stock_status = 'low_stock'
        else:
            self.stock_status = 'in_stock'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        self.update_stock_status()
        super().save(*args, **kwargs)
        from apps.inventory.services.alert import AlertService
        AlertService.check_and_create_alerts(self)
        
    def refresh_stock_from_warehouses(self):
        
        total = self.warehouse_stocks.filter(
            Warehouse__is_active=True
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        
        self.stock_quantity = total
        self.update_stock_status()
        self.save(update_fields=['stock_quantity', 'stock_status', 'updated_at'])
            
        
    def __str__(self):
        return f"{self.name} (SKU: {self.sku}) - Stock: {self.stock_quantity}"

