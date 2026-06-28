from django.db.models import QuerySet, Count


class CategoryQuerySet(QuerySet):

    
    def active(self):
        
        return self.filter(is_active=True)
    
    def with_product_count(self):
        
        return self.annotate(product_count=Count('products'))




