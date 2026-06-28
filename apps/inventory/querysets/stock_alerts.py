from django.db.models import QuerySet


class StockAlertQuerySet(QuerySet):

    
    def unresolved(self):
        """Alerts that need attention."""
        return self.filter(is_resolved=False)
    
    def resolved(self):
        """Already handled alerts."""
        return self.filter(is_resolved=True)
    
    def low_stock(self):
        """Only low stock alerts."""
        return self.filter(alert_type='low_stock')
    
    def out_of_stock(self):
        """Only out of stock alerts."""
        return self.filter(alert_type='out_of_stock')
    
    def for_product(self, product_id):
        """All alerts for a product."""
        return self.filter(product_id=product_id)
    
    def with_product(self):
        """Include product details."""
        return self.select_related('product', 'resolved_by')
    



