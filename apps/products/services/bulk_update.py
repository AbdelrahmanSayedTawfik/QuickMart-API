from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.products.models.product import Product
from apps.inventory.services.stock import InventoryService
from apps.products.services.cache import ProductCacheService


class BulkStockService:

    @staticmethod
    @transaction.atomic
    def update_stock(updates: list, user=None) -> dict:

        if not updates:
            raise ValidationError('No updates provided')
        
        product_ids = [u['product_id'] for u in updates]
        
        # Lock rows to prevent race conditions
        products = {
            p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }
        
        # Validate all first (fail fast)
        validated = []
        for update in updates:
            pid = update.get('product_id')
            new_stock = update.get('stock_quantity')
            
            if pid not in products:
                raise ValidationError(f'Product {pid} not found')
            
            if new_stock < 0:
                raise ValidationError(f'Invalid stock for product {pid}: {new_stock}')
            
            validated.append({
                'product': products[pid],
                'new_stock': new_stock
            })
        
        # Apply all updates
        updated_ids = []
        for item in validated:
            InventoryService.set_stock(
                product=item['product'],
                new_quantity=item['new_stock'],
                reason='Bulk stock update',
                user=user
            )
            updated_ids.append(item['product'].id)
        
        # Invalidate caches
        ProductCacheService.invalidate_product_list_all()
        
        return {
            'success': True,
            'updated_count': len(updated_ids),
            'updated_ids': updated_ids
        }