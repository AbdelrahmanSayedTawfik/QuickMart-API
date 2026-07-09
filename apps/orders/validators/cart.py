from django.core.exceptions import ValidationError
from apps.products.models.product import Product
from apps.products.models.warehouse_stock import WarehouseStock


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
    def validate_stock(product: Product, quantity: int, city: str = None) -> None:

        if not city:
            # No city known yet (e.g. user hasn't set one) — fall back to the
            # cached global total so the cart still works, checkout will do
            # the real per-city check later.
            if product.stock_quantity < quantity:
                raise ValidationError(
                    f'Not enough stock for "{product.name}". '
                    f'Available: {product.stock_quantity}, Requested: {quantity}'
                )
            return

        stock = WarehouseStock.objects.filter(
            Product=product,
            Warehouse__city__iexact=city,
            Warehouse__is_active=True
        ).order_by('-quantity').first()

        available = stock.quantity if stock else 0

        if available < quantity:
            raise ValidationError(
                f'Not enough stock for "{product.name}" in {city}. '
                f'Available: {available}, Requested: {quantity}'
            )

    @staticmethod
    def validate_new_quantity(product: Product, new_quantity: int, city: str = None) -> None:

        CartValidator.validate_quantity(new_quantity)
        CartValidator.validate_stock(product, new_quantity, city)