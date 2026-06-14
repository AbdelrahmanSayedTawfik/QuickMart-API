from django.core.exceptions import ValidationError
from apps.products.models.product import Product


class ProductValidator:

    MIN_PRICE = 0.01
    MAX_QUANTITY_PER_ITEM = 100
    
    @classmethod
    def validate_price(cls, price):
        if price < cls.MIN_PRICE:
            raise ValidationError(f'Price must be at least ${cls.MIN_PRICE}')
    
    @classmethod
    def validate_stock(cls, stock_quantity, status):
        
        if status == 'available' and stock_quantity <= 0:
            raise ValidationError(
                'Cannot set status to available with zero stock. '
                'Set status to out_of_stock or pre_order.'
            )
    
    @classmethod
    def validate_sku_unique(cls, sku, exclude_id=None):
        
        queryset = Product.objects.filter(sku=sku)
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        if queryset.exists():
            raise ValidationError(f'SKU "{sku}" already exists.')
    
    @classmethod
    def validate_quantity(cls, quantity: int):
        
        if quantity < 1:
            raise ValidationError('Quantity must be at least 1.')
        if quantity > cls.MAX_QUANTITY_PER_ITEM:
            raise ValidationError(f'Maximum {cls.MAX_QUANTITY_PER_ITEM} items per product.')
    
    @classmethod
    def validate_stock_availability(cls, product: Product, quantity: int):
        
        if product.stock_quantity < quantity:
            raise ValidationError(
                f'Not enough stock for "{product.name}". '
                f'Available: {product.stock_quantity}, Requested: {quantity}'
            )