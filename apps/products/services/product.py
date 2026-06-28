from django.db import transaction
from apps.products.models.product import Product
from apps.products.validators.product import ProductValidator
from apps.products.services.cache import ProductCacheService


class ProductService:

    @staticmethod
    @transaction.atomic
    def create_product(data: dict, seller) -> Product:

        # Validate business rules
        ProductValidator.validate_price(data['price'])
        if data.get('original_price', 0) > 0:
            ProductValidator.validate_price(data['original_price'])
        
        ProductValidator.validate_stock(data.get('stock_quantity', 0), data.get('status', 'draft'))
        ProductValidator.validate_sku_unique(data['sku'])
        
        # Create product
        product = Product.objects.create(seller=seller, **data)
        
        return product
    
    @staticmethod
    @transaction.atomic
    def update_product(product: Product, data: dict) -> Product:

        # Validate SKU uniqueness if changed
        sku = data.get('sku', product.sku)
        if sku != product.sku:
            ProductValidator.validate_sku_unique(sku, exclude_id=product.id)
        
        # Validate price if changed
        if 'price' in data:
            ProductValidator.validate_price(data['price'])
        if 'original_price' in data and data['original_price'] > 0:
            ProductValidator.validate_price(data['original_price'])
        
        # Validate stock/status combination
        stock = data.get('stock_quantity', product.stock_quantity)
        status = data.get('status', product.status)
        if 'stock_quantity' in data or 'status' in data:
            ProductValidator.validate_stock(stock, status)
        
        # Apply updates
        for key, value in data.items():
            setattr(product, key, value)
        
        product.save()
        

        
        return product
    
    @staticmethod
    @transaction.atomic
    def delete_product(product: Product) -> None:

        slug = product.slug
        product.delete()
        