from django.db.models import QuerySet, Prefetch


class OrderQuerySet(QuerySet):

    
    def for_user(self, user_id):
        
        return self.filter(user_id=user_id)
    
    def with_items(self):
        
        return self.prefetch_related(
            Prefetch(
                'items',
                queryset=self.model.items.related_model.objects.select_related('product')
            )
        )
    
    def with_status_logs(self):
        
        return self.prefetch_related('status_logs')
    
    def by_status(self, status):
        
        return self.filter(status=status)
    
    def recent(self):
        
        return self.order_by('-created_at')
    
    def pending(self):
        
        return self.filter(status='pending')
    
    def paid(self):
        
        return self.filter(status='paid')


# Attach to model
from apps.orders.models.order import Order
Order.objects = OrderQuerySet.as_manager()