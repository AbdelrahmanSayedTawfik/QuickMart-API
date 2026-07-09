from django.urls import path
from apps.orders.apis.checkout import CheckoutView
from apps.orders.apis.order_list import OrderListView
from apps.orders.apis.order_detail import OrderDetailView
from apps.orders.apis.order_cancel import OrderCancelView
from apps.orders.apis.mark_paid import MarkOrderPaidView

# orders/urls.py
urlpatterns = [
    # Checkout — now at /api/orders/checkout/
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    # Orders — now at /api/orders/<order_number>/
    path('', OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('<str:order_number>/mark-paid/', MarkOrderPaidView.as_view(), name='mark-paid'),
]