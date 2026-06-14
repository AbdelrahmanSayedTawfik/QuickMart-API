from rest_freamwork import serializers
from apps.orders.models.orderstatuslog import OrderStatusLog

class OrderStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusLog
        fields = ['id', 'order', 'previous_status', 'new_status', 'changed_at']
        read_only_fields = ['id', 'order', 'previous_status', 'new_status', 'changed_at']