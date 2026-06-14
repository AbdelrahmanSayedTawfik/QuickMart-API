from django.urls import path
from apps.orders.apis.cart import CartView
from apps.orders.apis.cart_add import CartAddItemView
from apps.orders.apis.cart_remove import CartRemoveItemView
from apps.orders.apis.cart_update import CartUpdateItemView
from apps.orders.apis.cart_clear import CartClearItemsView
from apps.orders.apis.checkout import CheckoutView
from apps.orders.apis.order_list import OrderListView
from apps.orders.apis.order_detail import OrderDetailView
from apps.orders.apis.order_cancel import OrderCancelView


urlpatterns = [
    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveItemView.as_view(), name='cart-remove'),
    path('cart/update/', CartUpdateItemView.as_view(), name='cart-update'),
    path('cart/clear/', CartClearItemsView.as_view(), name='cart-clear'),
    
    # Checkout
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    
    # Orders
    path('', OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
]