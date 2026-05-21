# apps/payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Create payment intent (step 1)
    path('create-intent/', views.create_payment_intent, name='create_payment_intent'),

    # Webhook (Stripe calls this)
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),

    # Check payment status
    path('<str:order_number>/', views.payment_status, name='payment_status'),
]