from django.db.models import QuerySet, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta


class StockMovementQuerySet(QuerySet):

    def for_product(self, product_id):
        """All movements for a specific product."""
        return self.filter(product_id=product_id)
    
    def by_type(self, movement_type):
        """Filter by movement type."""
        return self.filter(movement_type=movement_type)
    
    def by_user(self, user_id):
        """Who made the changes."""
        return self.filter(created_by_id=user_id)
    
    
    def today(self):
        """Today's movements."""
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        return self.filter(created_at__gte=today_start)
    
    def with_product_details(self):
        """Include product info (reduces queries)."""
        return self.select_related('product', 'created_by', 'order')
    

# Attach to model
from apps.inventory.models.stock_movement import StockMovement
StockMovement.objects = StockMovementQuerySet.as_manager()