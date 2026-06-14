from django.core.exceptions import ValidationError
from apps.products.models.product import Product


class StockValidator:

    
    @staticmethod
    def validate_quantity(quantity: int) -> None:

        if not isinstance(quantity, int):
            raise ValidationError('Quantity must be a whole number.')
        if quantity <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        if quantity > 10000:
            raise ValidationError('Quantity cannot exceed 10,000 per operation.')
    
    @staticmethod
    def validate_deduction(product: Product, quantity: int) -> None:

        if product.stock_quantity < quantity:
            raise ValidationError(
                f'Not enough stock for "{product.name}". '
                f'Available: {product.stock_quantity}, Requested: {quantity}'
            )
    
    @staticmethod
    def validate_new_stock(new_stock: int) -> None:

        if new_stock < 0:
            raise ValidationError('Stock cannot be negative.')
        if new_stock > 999999:
            raise ValidationError('Stock exceeds maximum allowed value.')
    
    @staticmethod
    def validate_reason(reason: str) -> None:

        if not reason or not reason.strip():
            raise ValidationError('Reason is required for stock movements.')
        if len(reason) > 255:
            raise ValidationError('Reason must be 255 characters or less.')