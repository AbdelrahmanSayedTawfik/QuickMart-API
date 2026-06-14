from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    try:
        from apps.orders.models import Order
        order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
        subject = f"Order Confirmation - Order #{order.id}"
        message = f"Dear {order.user.first_name},\n\nThank you for your order #{order.id}.\n\n"
        send_mail(
            subject = subject,
            message = message,
            from_email = 'sender@example.com',
            recipient_list = [order.user.email],
            fail_silently = False,
        )
        return f"Order confirmation email sent for order #{order.id}"
    except Order.DoesNotExist:
        raise self.retry(exc=Exception(f"Order with id {order_id} does not exist"), countdown=60)

@shared_task()
def send_payment_confirmation(order_id):
    
    from apps.orders.models import Order
    order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
    subject = f"Payment Confirmation - Order #{order.id}"
    message = f"Dear {order.user.first_name},\n\nYour payment for order #{order.id} has been received.\n\n"
    send_mail(
    subject = subject,
    message = message,
    from_email = 'sender@example.com',
    recipient_list = [order.user.email],
    )
    
@shared_task()
def send_status_update(order_id, new_status):
    
    from apps.orders.models import Order
    order = Order.objects.select_related('user').prefetch_related('items').get(id=order_id)
    subject = f"Order Status Update - Order #{order.id}"
    message = f"Dear {order.user.first_name},\n\nYour order #{order.id} status has been updated to '{new_status}'.\n\n"
    send_mail(
    subject = subject,
    message = message,
    from_email = 'sender@example.com',
    recipient_list = [order.user.email],
    ) 
