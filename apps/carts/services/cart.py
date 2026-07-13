from django.db import transaction

from apps.carts.models.cart import Cart
from apps.carts.models.cartitem import CartItem
from apps.carts.validators.cart import CartValidator
from apps.products.models.product import Product


class CartService:

    @staticmethod
    @transaction.atomic
    def get_or_create_cart(user) -> Cart:
        
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    @staticmethod
    @transaction.atomic
    def add_item(user, product_id: int, quantity: int,  city: str = None) -> CartItem:

        # Validate
        CartValidator.validate_quantity(quantity)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError('Product not found')
        
        CartValidator.validate_product_available(product)
        CartValidator.validate_stock(product, quantity, city)
        
        # Get cart
        cart = CartService.get_or_create_cart(user)
        
        # Get or create item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item exists — increment quantity
            new_quantity = item.quantity + quantity
            CartValidator.validate_stock(product, new_quantity, city)
            item.quantity = new_quantity
            item.save()
        
        return item
    
    @staticmethod
    @transaction.atomic
    def remove_item(user, product_id: int) -> None:
        
        cart = CartService.get_or_create_cart(user)
        
        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            item.delete()
        except CartItem.DoesNotExist:
            raise ValueError('Item not in cart')
    
    @staticmethod
    @transaction.atomic
    def update_quantity(user, product_id: int, quantity: int, city: str = None) -> CartItem:
        
        CartValidator.validate_quantity(quantity)
        
        cart = CartService.get_or_create_cart(user)
        
        try:
            item = CartItem.objects.select_related('product').get(
                cart=cart, product_id=product_id
            )
        except CartItem.DoesNotExist:
            raise ValueError('Item not in cart')
        
        if quantity == 0:
            item.delete()
            return None
        
        CartValidator.validate_new_quantity(item.product, quantity, city)
        item.quantity = quantity
        item.save()
        
        return item
    
    @staticmethod
    @transaction.atomic
    def clear_cart(user) -> None:
        
        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete()