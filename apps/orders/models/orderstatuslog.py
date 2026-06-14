from django.db import models
from apps.orders.models.order import Order
from apps.accounts.models.user import CustomUser

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='status_changes')
    
    def __str__(self):
        return f"Order {self.order.order_number} status changed from {self.previous_status} to {self.new_status} at {self.changed_at}" 