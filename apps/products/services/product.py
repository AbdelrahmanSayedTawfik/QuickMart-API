from django.db import transaction
from apps.products.models.product import Product
from apps.products.validators.product import ProductValidator
from apps.products.services.cache import ProductCacheService
from apps.warehouses.services.product_stock_sync import ProductStockSyncService


class ProductService:

    @staticmethod
    @transaction.atomic
    def create_product(data: dict, seller) -> Product:

        ProductValidator.validate_price(data['price'])
        if data.get('original_price', 0) > 0:
            ProductValidator.validate_price(data['original_price'])

        ProductValidator.validate_stock(data.get('stock_quantity', 0), data.get('status', 'draft'))
        ProductValidator.validate_sku_unique(data['sku'])

        initial_quantity = data.get('stock_quantity', 0)

        product = Product.objects.create(seller=seller, **data)

        # Direction 1: Product → WarehouseStock
        ProductStockSyncService.ensure_stock_for_product(
            product=product,
            quantity=initial_quantity,
            user=seller
        )

        return product

    @staticmethod
    @transaction.atomic
    def update_product(product: Product, data: dict) -> Product:

        # stock_quantity is not editable here — it's a cached total, only
        # ever correct when updated through StockService (warehouse operations)
        data = {k: v for k, v in data.items() if k != 'stock_quantity'}

        sku = data.get('sku', product.sku)
        if sku != product.sku:
            ProductValidator.validate_sku_unique(sku, exclude_id=product.id)

        if 'price' in data:
            ProductValidator.validate_price(data['price'])
        if 'original_price' in data and data['original_price'] > 0:
            ProductValidator.validate_price(data['original_price'])

        if 'status' in data:
            ProductValidator.validate_stock(product.stock_quantity, data['status'])

        for key, value in data.items():
            setattr(product, key, value)

        product.save()

        return product

    @staticmethod
    @transaction.atomic
    def delete_product(product: Product) -> None:
        slug = product.slug
        product.delete()