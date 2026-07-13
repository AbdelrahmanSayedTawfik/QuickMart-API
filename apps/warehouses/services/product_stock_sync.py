from apps.warehouses.models.warehouse import Warehouse
from apps.warehouses.services.warehouse_stock_service import StockService


class ProductStockSyncService:
    """
    Single source of truth for keeping Product and WarehouseStock in sync.
    Both directions (Product → WarehouseStock, WarehouseStock → Product)
    route through here so the logic never gets duplicated.
    """

    @staticmethod
    def ensure_stock_for_product(product, warehouse=None, quantity=0, threshold=5, user=None):
        """
        Direction: Product → WarehouseStock
        Called after a Product is created via the normal API.
        Creates/updates a WarehouseStock row and refreshes the product's cached total.
        """
        if warehouse is None:
            warehouse = Warehouse.objects.filter(is_default=True, is_active=True).first()

        if warehouse is None:
            # No default warehouse configured — product still exists,
            # just unstocked until a warehouse manager adds stock manually.
            return None

        stock = StockService.adjust(
            warehouse=warehouse,
            product=product,
            new_qty=quantity,
            reason='Initial stock on product creation',
            user=user
        )

        if threshold != stock.low_stock_threshold:
            stock.low_stock_threshold = threshold
            stock.save(update_fields=['low_stock_threshold'])

        product.refresh_stock_from_warehouses()
        return stock

    @staticmethod
    def sync_stock_for_import(product, warehouse, quantity, threshold=5, user=None):
        """
        Direction: WarehouseStock CSV/import → Product
        Called by importers after a Product has been created/resolved.
        Routes through StockService so the audit trail (WarehouseMovement)
        and Product.stock_quantity stay consistent, same as any other stock change.
        """
        stock = StockService.adjust(
            warehouse=warehouse,
            product=product,
            new_qty=quantity,
            reason='CSV import',
            user=user
        )

        if threshold != stock.low_stock_threshold:
            stock.low_stock_threshold = threshold
            stock.save(update_fields=['low_stock_threshold'])

        product.refresh_stock_from_warehouses()
        return stock