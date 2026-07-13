from apps.accounts.models.user import CustomUser
from apps.products.models.category import Category
from apps.products.models.product import Product
from apps.products.validators.product import ProductValidator
from .base import BaseImporter


class ProductImporter(BaseImporter):

    REQUIRED_COLUMNS = ['name', 'sku', 'price','warehouse_code', 'low_stock_threshold' ]
    OPTIONAL_COLUMNS = [
        'description',
        'original_price',
        'stock_quantity',
        'category_name',
        'status',
        'is_active',
        'is_featured',
    ]

    def check_permission(self) -> None:

        if not self.user:
            raise ValueError(
                'Authentication required to import products.'
            )

        user = self._resolve_user()

        if not user.is_superuser and user.role not in ('seller', 'admin'):
            raise ValueError(
                f'Permission denied. '
                f'User "{user.email}" has role "{user.role}". '
                f'Only seller or admin users can import products.'
            )



    def import_row(self, row: dict, row_num: int, update_existing: bool) -> str:

        seller = self._resolve_user()

        # --- Extract fields ---
        name           = self.get(row, 'name')
        sku            = self.get(row, 'sku')
        description    = self.get(row, 'description') or None
        price          = self.get_decimal(row, 'price')
        original_price = self.get_decimal(row, 'original_price', default=0)
        stock_quantity = self.get_int(row, 'stock_quantity', default=0)
        category_name  = self.get(row, 'category_name') or None
        status         = self.get(row, 'status', default='draft').lower()
        is_active      = self.get_bool(row, 'is_active', default=True)
        is_featured    = self.get_bool(row, 'is_featured', default=False)
        warehouse_code = self.get(row, 'warehouse_code') or None
        low_stock_threshold = self.get_int(row, 'low_stock_threshold', default=5)

        # --- Field validation ---
        if not name:
            raise ValueError('"name" is required.')
        if not sku:
            raise ValueError('"sku" is required.')
        if not price:
            raise ValueError('"price" is required.')
        if not warehouse_code:
            raise ValueError('"warehouse_code" is required.')

        warehouse = self._resolve_warehouse(warehouse_code)

        ProductValidator.validate_price(price)
        if original_price > 0:
            ProductValidator.validate_price(original_price)

        valid_statuses = ('draft', 'available', 'discontinued')
        if status not in valid_statuses:
            raise ValueError(
                f'"status" must be one of {valid_statuses}, got: "{status}"'
            )

        category = self._resolve_category(category_name)

        # --- Create or update ---
        try:
            product = Product.objects.get(sku=sku)

            if update_existing:
                # Sellers can only update their own products
                if not seller.is_superuser and seller.role != 'admin':
                    if product.seller != seller:
                        raise ValueError(
                            f'Permission denied. '
                            f'SKU "{sku}" belongs to "{product.seller.email}". '
                            f'You cannot modify another seller\'s product.'
                        )

                product.name           = name
                product.description    = description
                product.price          = price
                product.original_price = original_price
                product.stock_quantity = stock_quantity
                product.category       = category
                product.status         = status
                product.is_active      = is_active
                product.is_featured    = is_featured
                product.save()

                # --- Set warehouse stock for updated product ---
                if warehouse and stock_quantity > 0:
                    self._set_warehouse_stock(product, warehouse, stock_quantity, low_stock_threshold)

                return 'updated'

            # --- Product exists but update_existing=False ---
            # Still create warehouse stock if it doesn't exist
            if warehouse and stock_quantity > 0:
                self._set_warehouse_stock(product, warehouse, stock_quantity, low_stock_threshold)

            return 'skipped'

        except Product.DoesNotExist:
            # --- Create new product ---
            product = Product.objects.create(
                name=name,
                description=description,
                sku=sku,
                price=price,
                original_price=original_price,
                stock_quantity=stock_quantity,
                category=category,
                seller=seller,
                status=status,
                is_active=is_active,
                is_featured=is_featured,
            )

            # --- Set warehouse stock for NEW product ---
            # THIS IS THE FIX: moved INSIDE the except block, AFTER product is created
            if warehouse and stock_quantity > 0:
                self._set_warehouse_stock(product, warehouse, stock_quantity, low_stock_threshold)

            return 'created'

    def _resolve_warehouse(self, code):
        from apps.warehouses.models.warehouse import Warehouse
        try:
            return Warehouse.objects.get(code=code, is_active=True)
        except Warehouse.DoesNotExist:
            raise ValueError(f'Warehouse "{code}" not found')

    def _set_warehouse_stock(self, product, warehouse, quantity, threshold):
        from apps.warehouses.services.product_stock_sync import ProductStockSyncService
        ProductStockSyncService.sync_stock_for_import(
            product=product,
            warehouse=warehouse,
            quantity=quantity,
            threshold=threshold,
            user=self.user
        )

    def _resolve_user(self) -> CustomUser:

        if isinstance(self.user, str):
            try:
                return CustomUser.objects.get(email=self.user)
            except CustomUser.DoesNotExist:
                raise ValueError(f'User "{self.user}" not found.')
        return self.user

    def _resolve_category(self, category_name: str | None) -> Category | None:

        if not category_name:
            return None
        try:
            return Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise ValueError(
                f'Category "{category_name}" not found. '
                f'Import categories first before importing products.'
            )