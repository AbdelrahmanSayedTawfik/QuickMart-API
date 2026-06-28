from django.urls import path
from apps.payments.apis.create_intent import create_payment_intent
from apps.payments.apis.webhook import stripe_webhook
from apps.payments.apis.status import payment_status
from apps.payments.apis.hosted import hosted_checkout
from apps.payments.apis.success import payment_success,payment_cancel


urlpatterns = [
    # Create payment intent (called by frontend)
    path('create-intent/', create_payment_intent, name='create-payment-intent'), #DONE
    path('payments/<str:order_number>/checkout/',hosted_checkout , name='checkout'), #DONE
    # Webhook (called by Stripe)
    path('webhook/', stripe_webhook, name='stripe-webhook'),#DONE
    path('payments/success/', payment_success, name='payment-success'),
    path('payments/cancel/', payment_cancel, name='payment-cancel'),
    
    # Check payment status (called by frontend)
    path('<str:order_number>/', payment_status, name='payment-status'),#DONE
]