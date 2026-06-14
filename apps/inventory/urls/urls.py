from django.urls import path
from apps.inventory.apis.stock_movements import StockMovementListView, StockMovementDetailView
from apps.inventory.apis.stock_alerts import StockAlertListView, StockAlertDetailView, AlertSummaryView



urlpatterns = [
    
    path('movements/', StockMovementListView.as_view(), name='stock-movement-list'),
    path('movements/<int:pk>/', StockMovementDetailView.as_view(), name='stock-movement-detail'),
    
    
    path('alerts/', StockAlertListView.as_view(), name='stock-alert-list'),
    path('alerts/summary/', AlertSummaryView.as_view(), name='stock-alert-summary'),
    path('alerts/<int:pk>/', StockAlertDetailView.as_view(), name='stock-alert-detail'),
    

]