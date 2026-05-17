from django.urls import path , include
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddItemView.as_view(), name='cart-add-item'),
    path('cart/remove/', views.CartRemoveItemView.as_view(), name='cart-remove-item'),
    path('cart/update/', views.CartUpdateItemView.as_view(), name='cart-update-item'),
    path('cart/clear/', views.CartClearItemsView.as_view(), name='cart-clear-items'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<order_number>/cancel/', views.OrderRemoveView.as_view(), name='order-cancel'),
]