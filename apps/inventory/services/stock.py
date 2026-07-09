from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.products.models.product import Product
from apps.warehouses.models.warehouse import Warehouse
from apps.warehouses.models.warehouse_stock import WarehouseStock
from apps.inventory.models.stock_movement import StockMovement
from apps.inventory.validators.stock import StockValidator
from apps.inventory.services.alert import AlertService


class InventoryService:

    @staticmethod
    def _check_alerts(product):
        AlertService.check_and_create_alerts(product)

    @staticmethod
    def _refresh_product_total(product: Product):
        product.stock_quantity = WarehouseStock.get_total_stock(product.id)
        product.save(update_fields=['stock_quantity', 'stock_status', 'updated_at'])

    @staticmethod
    def _resolve_warehouse(product: Product, city: str) -> Warehouse:
        stock = WarehouseStock.objects.filter(
            Product=product,
            Warehouse__city__iexact=city,
            Warehouse__is_active=True,
            quantity__gt=0
        ).select_related('Warehouse').order_by('-quantity').first()

        if not stock:
            raise ValidationError(f"'{product.name}' is not available for delivery to {city}.")
        return stock.Warehouse

    @staticmethod
    @transaction.atomic
    def deduct_stock(product: Product, quantity: int, reason: str, user=None, order=None, order_item=None) -> StockMovement:
        StockValidator.validate_quantity(quantity)
        StockValidator.validate_reason(reason)

        city = order.delivery_city if order else None
        if not city:
            raise ValidationError("Cannot deduct stock without a delivery city.")

        warehouse = InventoryService._resolve_warehouse(product, city)

        stock = WarehouseStock.objects.select_for_update().get(Warehouse=warehouse, Product=product)
        if stock.quantity < quantity:
            raise ValidationError(
                f"Insufficient stock for '{product.name}' at {warehouse.name}. "
                f"Available: {stock.quantity}, Required: {quantity}"
            )

        old_quantity = stock.quantity
        stock.quantity -= quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        if order_item is not None:
            order_item.fulfillment_warehouse = warehouse
            order_item.save(update_fields=['fulfillment_warehouse'])

        InventoryService._refresh_product_total(product)

        movement = StockMovement.objects.create(
            product=product, movement_type='out', quantity=quantity,
            previous_stock=old_quantity, new_stock=stock.quantity,
            reason=reason, created_by=user, order=order
        )
        InventoryService._check_alerts(product)
        return movement

    @staticmethod
    @transaction.atomic
    def return_stock(product: Product, quantity: int, reason: str, user=None, order=None, warehouse=None) -> StockMovement:
        StockValidator.validate_quantity(quantity)
        StockValidator.validate_reason(reason)

        if warehouse is None:
            raise ValidationError("Cannot return stock without knowing which warehouse to credit.")

        stock, _ = WarehouseStock.objects.select_for_update().get_or_create(
            Warehouse=warehouse, Product=product, defaults={'quantity': 0}
        )

        old_quantity = stock.quantity
        stock.quantity += quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        InventoryService._refresh_product_total(product)

        movement = StockMovement.objects.create(
            product=product, movement_type='return', quantity=quantity,
            previous_stock=old_quantity, new_stock=stock.quantity,
            reason=reason, created_by=user, order=order
        )
        InventoryService._check_alerts(product)
        return movement

    @staticmethod
    def check_availability(product_id: int, requested_quantity: int, city: str = None) -> dict:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return {'available': False, 'message': 'Product not found', 'current_stock': 0, 'can_fulfill': 0}

        if product.status != 'available':
            return {'available': False, 'message': f'Product is {product.status}', 'current_stock': 0, 'can_fulfill': 0}

        if not city:
            return {'available': False, 'message': 'City required to check availability', 'current_stock': 0, 'can_fulfill': 0}

        stock = WarehouseStock.objects.filter(
            Product=product, Warehouse__city__iexact=city, Warehouse__is_active=True
        ).order_by('-quantity').first()

        current = stock.quantity if stock else 0

        if current < requested_quantity:
            return {
                'available': False,
                'message': f'Only {current} available in {city}. You requested {requested_quantity}',
                'current_stock': current,
                'can_fulfill': current
            }

        return {'available': True, 'message': 'In stock', 'current_stock': current, 'can_fulfill': requested_quantity}