from django.urls import path
from apps.carts.apis.cart import CartView
from apps.carts.apis.cart_add import CartAddItemView
from apps.carts.apis.cart_remove import CartRemoveItemView
from apps.carts.apis.cart_update import CartUpdateItemView
from apps.carts.apis.cart_clear import CartClearItemsView


# orders/urls.py
urlpatterns = [
    # Cart — now at /api/cart/
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveItemView.as_view(), name='cart-remove'),
    path('cart/update/', CartUpdateItemView.as_view(), name='cart-update'),
    path('cart/clear/', CartClearItemsView.as_view(), name='cart-clear'),
]