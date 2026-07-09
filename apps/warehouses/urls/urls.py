from django.urls import path
from apps.warehouses.apis.warehouse import WarehouseListCreateView,WarehouseDetailView
from apps.warehouses.apis.warehouse_stock import ProductStockSummaryView, ShipCheckView,WarehouseStockListView,StockInView,StockOutView,StockTransferView,StockAdjustmentView
from apps.warehouses.apis.warehouse_movement import WarehouseMovementListView,WarehouseMovementDetailView

urlpatterns = [
    
    # Warehouses
    path('warehouse/', WarehouseListCreateView.as_view(), name='warehouse-list'),
    path('warehouse/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
    
    # Stock
    path('warehouse/stock/product/<int:product_id>/', ProductStockSummaryView.as_view(), name='product-stock-summary'),
    path('warehouse/<int:warehouse_id>/stock/', WarehouseStockListView.as_view(), name='warehouse-stock-list'),
    
    # Stock operations ← ALL NEW
    path('warehouse/<int:warehouse_id>/stock/in/', StockInView.as_view(), name='stock-in'),
    path('warehouse/<int:warehouse_id>/stock/out/', StockOutView.as_view(), name='stock-out'),
    path('warehouse/<int:warehouse_id>/stock/transfer/', StockTransferView.as_view(), name='stock-transfer'),
    
    # Adjustment
    path('warehouse/<int:warehouse_id>/stock/<int:product_id>/adjust/', StockAdjustmentView.as_view(), name='stock-adjust'),
    
    # Movements
    path('warehouse/movements/', WarehouseMovementListView.as_view(), name='movement-list'),
    path('warehouse/movements/<int:pk>/', WarehouseMovementDetailView.as_view(), name='movement-detail'),
    
    path('products/<int:product_id>/ship/',ShipCheckView.as_view(),name='ship-check'),
    
    

    
]