from django.urls import path
from apps.products.apis.products import ProductListCreateView, ProductRetrieveUpdateDestroyView
from apps.products.apis.categories import CategoryListCreateView, CategoryRetrieveUpdateDestroyView
from apps.products.apis.reviews import ReviewListCreateView, ReviewRetrieveUpdateDestroyView
from apps.products.apis.bulk_stock import bulk_update_stock


urlpatterns = [
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    
    
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    
    
    path('products/<slug:slug>/reviews/', ReviewListCreateView.as_view(), name='review-list'),
    
    
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail'),
    
    
    path('products/bulk-stock/', bulk_update_stock, name='bulk-stock'),
]