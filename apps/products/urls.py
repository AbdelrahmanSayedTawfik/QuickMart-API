from django.urls import path , include
from . import views
urlpatterns = [
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:slug>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<slug:slug>/', views.ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/<slug:slug>/reviews/', views.ReviewListCreateView.as_view(), name='product-reviews'),
    path('reviews/<int:pk>/', views.ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail'),
]