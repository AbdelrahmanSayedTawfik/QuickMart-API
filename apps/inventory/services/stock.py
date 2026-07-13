from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models

from apps.products.models.product import Product
from apps.warehouses.models.warehouse import Warehouse
from apps.warehouses.models.warehouse_stock import WarehouseStock
from apps.warehouses.models.warehouse_movement import WarehouseMovement
from apps.inventory.models.stock_movement import StockMovement
from apps.inventory.services.alert import AlertService


class InventoryService:
    
    @staticmethod
    def _check_alerts(product: Product):
        """Trigger low-stock alerts after any stock change."""
        AlertService.check_and_create_alerts(product)

    @staticmethod
    def _resolve_warehouse_for_city(product: Product, city: str) -> Warehouse:
        """
        Find the best warehouse to fulfill an order.
        Priority: Most stock in the customer's city.
        """
        if not city:
            raise ValidationError("Delivery city is required to deduct stock.")

        stock = WarehouseStock.objects.filter(
            Product=product,
            Warehouse__city__iexact=city,
            Warehouse__is_active=True,
            quantity__gt=0
        ).select_related('Warehouse').order_by('-quantity').first()

        if not stock:
            # Check what cities DO have stock (for error message)
            available_cities = WarehouseStock.objects.filter(
                Product=product,
                Warehouse__is_active=True,
                quantity__gt=0
            ).values_list('Warehouse__city', flat=True).distinct()

            cities_list = ', '.join(filter(None, available_cities)) or 'nowhere'

            raise ValidationError(
                f"'{product.name}' is not available for delivery to {city}. "
                f"Available in: {cities_list}"
            )

        return stock.Warehouse

    @staticmethod
    def _log_warehouse_movement(
        movement_type: str,
        product: Product,
        quantity: int,
        warehouse: Warehouse,
        stock_before: int,
        stock_after: int,
        reason: str,
        user=None,
        order=None,
        reference_id: str = ''
    ) -> WarehouseMovement:
        """Create warehouse-level audit record."""
        return WarehouseMovement.objects.create(
            movement_type=movement_type,
            product=product,
            quantity=quantity,
            destination_warehouse=warehouse if movement_type in ('in', 'transfer_in') else None,
            source_warehouse=warehouse if movement_type in ('out', 'transfer_out') else None,
            destination_stock_before=stock_before if movement_type in ('in', 'transfer_in') else None,
            source_stock_before=stock_before if movement_type in ('out', 'transfer_out') else None,
            dest_after=stock_after if movement_type in ('in', 'transfer_in') else None,
            source_after=stock_after if movement_type in ('out', 'transfer_out') else None,
            reference_id=reference_id or (order.order_number if order else ''),
            notes=reason,
            created_by=user
        )

    @staticmethod
    def _log_stock_movement(
        product: Product,
        movement_type: str,
        quantity: int,
        previous_stock: int,
        new_stock: int,
        reason: str,
        user=None,
        order=None
    ) -> StockMovement:
        """Create inventory-wide audit record."""
        return StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reason=reason,
            created_by=user,
            order=order
        )

    # ── PUBLIC API: DEDUCT STOCK (called when order is paid) ──

    @staticmethod
    @transaction.atomic
    def deduct_stock(
        product: Product,
        quantity: int,
        reason: str,
        user=None,
        order=None,
        order_item=None,
        city: str = None
    ) -> tuple[StockMovement, WarehouseMovement]:
        """
        Deduct stock from warehouse in customer's city.
        Called by OrderService.mark_as_paid().
        """
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if not reason or not str(reason).strip():
            raise ValidationError("A reason is required")

        # Step 1: Find warehouse by city
        warehouse = InventoryService._resolve_warehouse_for_city(product, city or order.delivery_city)

        # Step 2: Lock row (prevents race conditions)
        stock = WarehouseStock.objects.select_for_update().get(
            Warehouse=warehouse,
            Product=product
        )

        # Step 3: Validate sufficient stock
        if stock.quantity < quantity:
            raise ValidationError(
                f"Insufficient stock for '{product.name}' at {warehouse.name}. "
                f"Available: {stock.quantity}, Required: {quantity}"
            )

        # Step 4: Deduct
        stock_before = stock.quantity
        stock.quantity -= quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        # Step 5: Record fulfillment warehouse on order item
        if order_item is not None:
            order_item.fulfillment_warehouse = warehouse
            order_item.save(update_fields=['fulfillment_warehouse'])

        # Step 6: Create audit records
        wh_movement = InventoryService._log_warehouse_movement(
            movement_type='out',
            product=product,
            quantity=quantity,
            warehouse=warehouse,
            stock_before=stock_before,
            stock_after=stock.quantity,
            reason=reason,
            user=user,
            order=order,
            reference_id=order.order_number if order else ''
        )

        global_before = product.stock_quantity
        global_after = global_before - quantity

        inv_movement = InventoryService._log_stock_movement(
            product=product,
            movement_type='out',
            quantity=quantity,
            previous_stock=global_before,
            new_stock=global_after,
            reason=reason,
            user=user,
            order=order
        )

        # Step 7: Check alerts
        InventoryService._check_alerts(product)

        return inv_movement, wh_movement

    # ── PUBLIC API: RETURN STOCK (called when order cancelled/refunded) ──

    @staticmethod
    @transaction.atomic
    def return_stock(
        product: Product,
        quantity: int,
        reason: str,
        user=None,
        order=None,
        warehouse: Warehouse = None
    ) -> tuple[StockMovement, WarehouseMovement]:
        """
        Return stock to warehouse (e.g., order cancelled).
        If no warehouse provided, returns to default warehouse.
        """
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if not reason or not str(reason).strip():
            raise ValidationError("A reason is required")

        if warehouse is None:
            warehouse = Warehouse.objects.filter(is_default=True).first()
            if not warehouse:
                raise ValidationError("No default warehouse configured for returns.")

        # Lock and update warehouse stock
        stock, created = WarehouseStock.objects.select_for_update().get_or_create(
            Warehouse=warehouse,
            Product=product,
            defaults={'quantity': 0, 'low_stock_threshold': 5}
        )

        stock_before = stock.quantity
        stock.quantity += quantity
        stock.save(update_fields=['quantity', 'updated_at'])

        # Create audit records
        wh_movement = InventoryService._log_warehouse_movement(
            movement_type='in',
            product=product,
            quantity=quantity,
            warehouse=warehouse,
            stock_before=stock_before,
            stock_after=stock.quantity,
            reason=reason,
            user=user,
            order=order,
            reference_id=order.order_number if order else ''
        )

        global_before = product.stock_quantity
        global_after = global_before + quantity

        inv_movement = InventoryService._log_stock_movement(
            product=product,
            movement_type='return',
            quantity=quantity,
            previous_stock=global_before,
            new_stock=global_after,
            reason=reason,
            user=user,
            order=order
        )

        InventoryService._check_alerts(product)

        return inv_movement, wh_movement

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