from django.urls import path
from apps.products.apis.products import ProductListCreateView, ProductRetrieveUpdateDestroyView
from apps.products.apis.categories import CategoryListCreateView, CategoryRetrieveUpdateDestroyView
from apps.products.apis.reviews import ReviewListCreateView, ReviewRetrieveUpdateDestroyView
from apps.products.apis.bulk_stock import bulk_update_stock
from apps.products.apis.csv_import import ProductCSVCreateView,ProductCSVUpdateView,CategoryCSVCreateView,CategoryCSVUpdateView,CSVTemplateView
from apps.products.apis.product_image import (
    ProductImageUploadView,         # Single upload
    ProductImageBulkUploadView,     # Bulk upload
    ProductImageListView,           # List images
    ProductImageDetailView,         # Single image CRUD
)

from apps.products.apis.warehouse import WarehouseListCreateView,WarehouseDetailView
from apps.products.apis.warehouse_stock import ProductStockSummaryView, ShipCheckView,WarehouseStockListView,StockInView,StockOutView,StockTransferView,StockAdjustmentView
from apps.products.apis.warehouse_movement import WarehouseMovementListView,WarehouseMovementDetailView

urlpatterns = [
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list'), #DONE
    path('categories/<slug:slug>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),#DONE
    
    
    path('products/', ProductListCreateView.as_view(), name='product-list'), #DONE
    
    path('products/bulk-stock/', bulk_update_stock, name='bulk-stock'), #DONE 
    
    path('products/<slug:slug>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'), #DONE
    
    
    path('products/<slug:slug>/reviews/', ReviewListCreateView.as_view(), name='review-list'), #DONE
    
    path('products/<int:product_id>/ship/',ShipCheckView.as_view(),name='ship-check'),
    
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail'), #DONE
    
    path('import/csv/products/create/',ProductCSVCreateView.as_view(),name='csv-products-create'),#DONE

    path('import/csv/products/update/',ProductCSVUpdateView.as_view(),name='csv-products-update'),#DONE
    
    path('import/csv/categories/create/',CategoryCSVCreateView.as_view(),name='csv-categories-create'),#DONE
    
    path('import/csv/categories/update/',CategoryCSVUpdateView.as_view(),name='csv-categories-update'),#DONE

    # GET                               → JSON overview of all models
    # GET ?model=products               → downloads products_template.csv
    # GET ?model=categories             → downloads categories_template.csv
    # GET ?model=products&format=json   → JSON column info
    path('import/csv/template/',CSVTemplateView.as_view(),name='csv-template'),  #DONE
    
    
    path('<int:product_id>/images/upload/', ProductImageUploadView.as_view(), name='product-image-upload'),
    path('<int:product_id>/images/bulk-upload/', ProductImageBulkUploadView.as_view(), name='product-image-bulk-upload'),
    path('<int:product_id>/images/', ProductImageListView.as_view(), name='product-image-list'),
    path('images/<int:pk>/', ProductImageDetailView.as_view(), name='product-image-detail'),
    
    
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
    
    

    
]