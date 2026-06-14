from django.urls import path
from apps.payments.apis.create_intent import create_payment_intent
from apps.payments.apis.webhook import stripe_webhook
from apps.payments.apis.status import payment_status


urlpatterns = [
    # Create payment intent (called by frontend)
    path('create-intent/', create_payment_intent, name='create-payment-intent'),
    
    # Webhook (called by Stripe)
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    
    # Check payment status (called by frontend)
    path('<str:order_number>/', payment_status, name='payment-status'),
]