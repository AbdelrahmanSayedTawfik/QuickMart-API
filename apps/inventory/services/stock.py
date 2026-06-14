from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.products.models.product import Product
from apps.inventory.models.stock_movement import StockMovement
from apps.inventory.validators.stock import StockValidator


class InventoryService:

    # ── STOCK DEDUCTION (when customer buys) ──
    
    @staticmethod
    @transaction.atomic
    def deduct_stock(
        product: Product,
        quantity: int,
        reason: str,
        user=None,
        order=None
    ) -> StockMovement:

        # Validate everything FIRST (fail fast)
        StockValidator.validate_quantity(quantity)
        StockValidator.validate_deduction(product, quantity)
        StockValidator.validate_reason(reason)
        
        # Perform the deduction
        old_quantity = product.stock_quantity
        product.stock_quantity -= quantity
        product.save()  # Triggers update_stock_status() in Product model
        
        # Create audit trail
        movement = StockMovement.objects.create(
            product=product,
            movement_type='out',
            quantity=quantity,
            previous_stock=old_quantity,
            new_stock=product.stock_quantity,
            reason=reason,
            created_by=user,
            order=order
        )
        
        return movement
    
    # ── STOCK ADDITION (new shipment, return, cancellation) ──
    
    @staticmethod
    @transaction.atomic
    def add_stock(
        product: Product,
        quantity: int,
        reason: str,
        user=None,
        order=None
    ) -> StockMovement:

        StockValidator.validate_quantity(quantity)
        StockValidator.validate_reason(reason)
        
        old_quantity = product.stock_quantity
        product.stock_quantity += quantity
        product.save()
        
        movement = StockMovement.objects.create(
            product=product,
            movement_type='in',
            quantity=quantity,
            previous_stock=old_quantity,
            new_stock=product.stock_quantity,
            reason=reason,
            created_by=user,
            order=order
        )
        
        return movement
    
    # ── STOCK ADJUSTMENT (inventory count, damaged goods) ──
    
    @staticmethod
    @transaction.atomic
    def set_stock(
        product: Product,
        new_quantity: int,
        reason: str,
        user=None
    ) -> StockMovement:

        StockValidator.validate_new_stock(new_quantity)
        StockValidator.validate_reason(reason)
        
        old_quantity = product.stock_quantity
        
        if old_quantity == new_quantity:
            raise ValidationError('New stock is same as current stock. No change needed.')
        
        product.stock_quantity = new_quantity
        product.save()
        
        # Determine movement type based on change direction
        if new_quantity > old_quantity:
            movement_type = 'in'
        else:
            movement_type = 'adjustment'
        
        movement = StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=abs(new_quantity - old_quantity),
            previous_stock=old_quantity,
            new_stock=new_quantity,
            reason=reason,
            created_by=user
        )
        
        return movement
    
    # ── STOCK RETURN (customer returns item) ──
    
    @staticmethod
    @transaction.atomic
    def return_stock(
        product: Product,
        quantity: int,
        reason: str,
        user=None,
        order=None
    ) -> StockMovement:

        StockValidator.validate_quantity(quantity)
        StockValidator.validate_reason(reason)
        
        old_quantity = product.stock_quantity
        product.stock_quantity += quantity
        product.save()
        
        movement = StockMovement.objects.create(
            product=product,
            movement_type='return',
            quantity=quantity,
            previous_stock=old_quantity,
            new_stock=product.stock_quantity,
            reason=reason,
            created_by=user,
            order=order
        )
        
        return movement
    
    # ── AVAILABILITY CHECK ──
    
    @staticmethod
    def check_availability(product_id: int, requested_quantity: int) -> dict:

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return {
                'available': False,
                'message': 'Product not found',
                'current_stock': 0,
                'can_fulfill': 0
            }
        
        if product.status != 'available':
            return {
                'available': False,
                'message': f'Product is {product.status}',
                'current_stock': product.stock_quantity,
                'can_fulfill': 0
            }
        
        if product.stock_quantity < requested_quantity:
            return {
                'available': False,
                'message': (
                    f'Only {product.stock_quantity} available. '
                    f'You requested {requested_quantity}'
                ),
                'current_stock': product.stock_quantity,
                'can_fulfill': product.stock_quantity
            }
        
        return {
            'available': True,
            'message': 'In stock',
            'current_stock': product.stock_quantity,
            'can_fulfill': requested_quantity
        }
    