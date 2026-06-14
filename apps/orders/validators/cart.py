from django.core.exceptions import ValidationError
from apps.products.models.product import Product


class CartValidator:

    MAX_QUANTITY_PER_ITEM = 100
    
    @staticmethod
    def validate_quantity(quantity: int) -> None:
        
        if not isinstance(quantity, int):
            raise ValidationError('Quantity must be a whole number.')
        if quantity < 1:
            raise ValidationError('Quantity must be at least 1.')
        if quantity > CartValidator.MAX_QUANTITY_PER_ITEM:
            raise ValidationError(f'Maximum {CartValidator.MAX_QUANTITY_PER_ITEM} items per product.')
    
    @staticmethod
    def validate_product_available(product: Product) -> None:
        
        if product.status != 'available':
            raise ValidationError(
                f'Product "{product.name}" is not available (status: {product.status})'
            )
    
    @staticmethod
    def validate_stock(product: Product, quantity: int) -> None:
        
        if product.stock_quantity < quantity:
            raise ValidationError(
                f'Not enough stock for "{product.name}". '
                f'Available: {product.stock_quantity}, Requested: {quantity}'
            )
    
    @staticmethod
    def validate_new_quantity(product: Product, new_quantity: int) -> None:
        
        CartValidator.validate_quantity(new_quantity)
        CartValidator.validate_stock(product, new_quantity)