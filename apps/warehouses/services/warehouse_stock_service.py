from django.db import transaction
from apps.products.models.product import Product
from apps.warehouses.models.warehouse import Warehouse
from apps.warehouses.models.warehouse_stock import WarehouseStock
from apps.warehouses.models.warehouse_movement import WarehouseMovement


class StockError(ValueError):
    pass


class StockService:

    @staticmethod
    def _log(**kwargs):
        """Write audit record."""
        return WarehouseMovement.objects.create(**kwargs)

    @staticmethod
    @transaction.atomic
    def add_stock_external_src(warehouse, product, qty, ref='', note='', user=None):
        stock, _ = WarehouseStock.objects.select_for_update().get_or_create(
            Warehouse=warehouse, Product=product,
            defaults={'quantity': 0, 'low_stock_threshold': 5}
        )
        before = stock.quantity
        stock.quantity += qty
        stock.save(update_fields=('quantity', 'updated_at'))

        StockService._log(
            movement_type='in', product=product, quantity=qty,
            destination_warehouse=warehouse,
            destination_stock_before=before, dest_after=stock.quantity,
            reference_id=ref, notes=note or f'Received at {warehouse.name}',
            created_by=user
        )
        return stock

    @staticmethod
    @transaction.atomic
    def remove_stock_external_src(warehouse, product, qty, ref='', note='', user=None):
        try:
            stock = WarehouseStock.objects.select_for_update().get(Warehouse=warehouse, Product=product)
        except WarehouseStock.DoesNotExist:
            raise StockError(f'No stock for {product.name} at {warehouse.name}')

        before = stock.quantity
        if qty > stock.quantity:
            raise StockError(f'Not enough at {warehouse.name}. Have: {stock.quantity}, Need: {qty}')

        stock.quantity -= qty
        stock.save(update_fields=('quantity', 'updated_at'))

        StockService._log(
            movement_type='out', product=product, quantity=qty,
            source_warehouse=warehouse,
            source_stock_before=before, source_after=stock.quantity,
            reference_id=ref, notes=note or f'Dispatched from {warehouse.name}',
            created_by=user
        )
        return stock

    @staticmethod
    @transaction.atomic
    def transfer_warehouses(source, destination, product, qty, ref='', note='', user=None):
        wh_ids = sorted((source.id, destination.id))
        stocks = WarehouseStock.objects.select_for_update().filter(
            Warehouse_id__in=wh_ids,
            Product=product
        ).order_by('Warehouse_id')

        stock_map = {s.Warehouse_id: s for s in stocks}

        src = stock_map.get(source.id)
        if not src:
            raise StockError(f'No stock for {product.name} at {source.name}')

        dst = stock_map.get(destination.id)
        if not dst:
            dst = WarehouseStock.objects.create(
                Warehouse=destination,
                Product=product,
                quantity=0,
                low_stock_threshold=5
            )

        src_before, dst_before = src.quantity, dst.quantity

        if qty > src.quantity:
            raise StockError(f'Not enough at {source.name}. Have: {src.quantity}, Need: {qty}')

        src.quantity -= qty
        dst.quantity += qty

        src.save(update_fields=('quantity', 'updated_at'))
        dst.save(update_fields=('quantity', 'updated_at'))

        for move_type, wh_note in (('transfer_out', f'To {destination.name}'), ('transfer_in', f'From {source.name}')):
            StockService._log(
                movement_type=move_type,
                product=product,
                quantity=qty,
                source_warehouse=source,
                destination_warehouse=destination,
                source_stock_before=src_before,
                destination_stock_before=dst_before,
                source_after=src.quantity,
                dest_after=dst.quantity,
                reference_id=ref,
                notes=note or wh_note,
                created_by=user
            )

        return src, dst

    @staticmethod
    @transaction.atomic
    def adjust(warehouse, product, new_qty, reason='', user=None):
        stock, _ = WarehouseStock.objects.select_for_update().get_or_create(
            Warehouse=warehouse, Product=product,
            defaults={'quantity': 0, 'low_stock_threshold': 5}
        )
        old = stock.quantity
        diff = new_qty - old

        stock.quantity = new_qty
        stock.save(update_fields=('quantity', 'updated_at'))

        if diff != 0:
            StockService._log(
                movement_type='adjustment', product=product, quantity=abs(diff),
                source_warehouse=warehouse if diff < 0 else None,
                destination_warehouse=warehouse if diff > 0 else None,
                source_stock_before=old, destination_stock_before=old,
                source_after=stock.quantity if diff < 0 else None,
                dest_after=stock.quantity if diff > 0 else None,
                notes=reason or f'Adjusted: {old} → {new_qty}',
                created_by=user
            )
        return stock

    @staticmethod
    def check_ship(product, user_city):
        if not user_city:
            return {'can_ship': False, 'reason': 'City not provided', 'warehouses': []}

        eligible = WarehouseStock.objects.filter(
            Product=product,
            Warehouse__city__iexact=user_city,
            Warehouse__is_active=True,
            quantity__gt=0
        ).select_related('Warehouse').order_by('-quantity')

        if not eligible.exists():
            others = WarehouseStock.objects.filter(
                Product=product,
                Warehouse__is_active=True,
                quantity__gt=0
            ).values_list('Warehouse__city', flat=True).distinct()
            return {
                'can_ship': False,
                'reason': f'Not available in {user_city}',
                'other_cities': list(filter(None, others)),
                'warehouses': []
            }

        return {
            'can_ship': True,
            'warehouses': [
                {'id': s.Warehouse.id, 'name': s.Warehouse.name, 'city': s.Warehouse.city,
                 'qty': s.quantity, 'is_low': s.is_low_stock()}
                for s in eligible
            ]
        }

    @staticmethod
    def summarize(product_id):
        """Stock breakdown across all warehouses."""
        stocks = WarehouseStock.objects.filter(
            Product_id=product_id,
            Warehouse__is_active=True
        ).select_related('Warehouse')

        return {
            'total': sum(s.quantity for s in stocks),
            'warehouses': [
                {
                    'name': s.Warehouse.name, 'code': s.Warehouse.code, 'city': s.Warehouse.city,
                    'qty': s.quantity,
                    'is_low': s.is_low_stock(), 'is_empty': s.is_out_of_stock(),
                    'threshold': s.low_stock_threshold,
                }
                for s in stocks
            ]
        }

    @staticmethod
    def get_default_stock(product_id):
        """Get or create stock in default warehouse."""
        default_wh = Warehouse.objects.filter(is_default=True).first()
        if not default_wh:
            return None
        stock, _ = WarehouseStock.objects.get_or_create(
            Warehouse=default_wh,
            Product_id=product_id,
            defaults={'quantity': 0, 'low_stock_threshold': 5}
        )
        return stock