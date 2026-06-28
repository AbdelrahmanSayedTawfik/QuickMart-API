from django.db.models import QuerySet, Sum


class PaymentQuerySet(QuerySet):

    def succeeded(self):
        
        return self.filter(status='succeeded')
    
    def pending(self):
        
        return self.filter(status='pending')
    
    def failed(self):
        
        return self.filter(status='failed')
    
    def for_order(self, order_id):
        
        return self.filter(order_id=order_id)
    
    def for_user(self, user_id):
        
        return self.filter(order__user_id=user_id)
    
    def recent(self, days=30):
        
        from django.utils import timezone
        from datetime import timedelta
        return self.filter(created_at__gte=timezone.now() - timedelta(days=days))
    
    def total_revenue(self):
        
        return self.succeeded().aggregate(total=Sum('amount'))['total'] or 0
    
    def with_order_details(self):
        
        return self.select_related('order', 'order__user')



