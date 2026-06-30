from django.urls import path
from apps.payments.apis.create_intent import create_payment_intent
from apps.payments.apis.webhook import stripe_webhook
from apps.payments.apis.status import payment_status
from apps.payments.apis.hosted import hosted_checkout
from apps.payments.apis.success import payment_success,payment_cancel


urlpatterns = [
    path('create-intent/', create_payment_intent, name='create-payment-intent'),
    path('<str:order_number>/checkout/', hosted_checkout, name='checkout'),  
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('success/', payment_success, name='payment-success'),   
    path('cancel/', payment_cancel, name='payment-cancel'),      
    path('<str:order_number>/', payment_status, name='payment-status'),
    
]