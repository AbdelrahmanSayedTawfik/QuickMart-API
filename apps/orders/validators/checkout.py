from django.core.exceptions import ValidationError
from apps.carts.models.cart import Cart
from apps.warehouses.models.warehouse_stock import WarehouseStock


class CheckoutValidator:

    @staticmethod
    def validate_cart(user) -> Cart:
        try:
            cart = Cart.objects.prefetch_related('items', 'items__product').get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError('No cart found.')

        if not cart.items.exists():
            raise ValidationError('Cart is empty. Add items before checkout.')

        return cart

    @staticmethod
    def validate_address(data: dict) -> None:
        required = ['delivery_address', 'delivery_city', 'delivery_phone']
        missing = [f for f in required if not data.get(f) or not str(data.get(f)).strip()]
        if missing:
            raise ValidationError(f'Missing required fields: {", ".join(missing)}')

    @staticmethod
    def validate_stock(cart: Cart, city: str) -> None:
        from apps.orders.validators.cart import CartValidator

        for item in cart.items.select_related('product'):
            product = item.product
            CartValidator.validate_product_available(product)

            stock = WarehouseStock.objects.filter(
                Product=product,
                Warehouse__city__iexact=city,
                Warehouse__is_active=True
            ).order_by('-quantity').first()

            available = stock.quantity if stock else 0

            if available < item.quantity:
                raise ValidationError(
                    f"'{product.name}' is not available in {city}. "
                    f"Available: {available}, Requested: {item.quantity}"
                )