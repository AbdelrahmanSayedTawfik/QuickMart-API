from django.db import models
from apps.products.models.product import Product  


class ProductImage(models.Model):


    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images',help_text='The product this image belongs to')
    image = models.ImageField(upload_to='product_images/',help_text='Upload an image file (JPG, PNG, WebP)')
    alt_text = models.CharField(max_length=255,blank=True,null=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:

        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['product', 'is_main']),
        ]
        
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        main_marker = ' [MAIN]' if self.is_main else ''
        return f'{self.product.name}{main_marker} - {self.image.name}'