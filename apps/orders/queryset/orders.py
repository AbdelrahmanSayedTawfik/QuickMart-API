from django.db.models import QuerySet, Prefetch


class OrderQuerySet(QuerySet):

    
    def for_user(self, user):
        user_id = user.id if hasattr(user, 'id') else user
        return self.filter(user_id=user_id)
    
    def with_items(self):
        from apps.orders.models.orderitem import OrderItem  
        return self.prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
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



