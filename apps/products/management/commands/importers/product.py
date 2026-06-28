from apps.accounts.models.user import CustomUser
from apps.products.models.category import Category
from apps.products.models.product import Product
from apps.products.validators.product import ProductValidator
from .base import BaseImporter


class ProductImporter(BaseImporter):

    REQUIRED_COLUMNS = ['name', 'sku', 'price']
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

        # --- Field validation ---
        if not name:
            raise ValueError('"name" is required.')
        if not sku:
            raise ValueError('"sku" is required.')
        if not price:
            raise ValueError('"price" is required.')

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
                return 'updated'

            return 'skipped'

        except Product.DoesNotExist:
            Product.objects.create(
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
            return 'created'


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