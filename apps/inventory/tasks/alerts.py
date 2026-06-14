from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from apps.inventory.models.stock_alert import StockAlert


@shared_task
def send_low_stock_email(alert_id: int):

    try:
        alert = StockAlert.objects.select_related('product', 'product__seller').get(id=alert_id)
    except StockAlert.DoesNotExist:
        return
    
    product = alert.product
    seller = product.seller
    
    subject = f'⚠️ Low Stock Alert: {product.name}'
    message = f'''
    Hello {seller.username},
    
    Your product "{product.name}" (SKU: {product.sku}) is running low on stock.
    
    Current stock: {product.stock_quantity}
    Threshold: {alert.threshold}
    
    Please restock soon to avoid losing sales.
    
    ---
    QuickMart Inventory System
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[seller.email],
        fail_silently=True
    )
    
    # Mark as sent
    from django.utils import timezone
    alert.email_sent = True
    alert.email_sent_at = timezone.now()
    alert.save()


@shared_task
def send_out_of_stock_email(alert_id: int):

    try:
        alert = StockAlert.objects.select_related('product', 'product__seller').get(id=alert_id)
    except StockAlert.DoesNotExist:
        return
    
    product = alert.product
    
    send_mail(
        subject=f'🚨 OUT OF STOCK: {product.name}',
        message=f'''
        URGENT: Your product "{product.name}" is now OUT OF STOCK.
        
        Customers cannot purchase this item until you restock.
        
        SKU: {product.sku}
        Previous stock: {alert.stock_at_trigger}
        
        Restock immediately!
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[product.seller.email],
        fail_silently=True
    )
    
    alert.email_sent = True
    alert.email_sent_at = timezone.now()
    alert.save()


@shared_task
def daily_inventory_report():

    from apps.inventory.services.alert import AlertService
    
    summary = AlertService.get_alert_summary()
    
    if summary['total_unresolved'] > 0:
        send_mail(
            subject='📊 Daily Inventory Report',
            message=f'''
            Daily Inventory Summary:
            
            Unresolved Alerts: {summary['total_unresolved']}
            - Low Stock: {summary['low_stock']}
            - Out of Stock: {summary['out_of_stock']}
            - Back in Stock: {summary['back_in_stock']}
            
            Review at: {settings.SITE_URL}/admin/inventory/
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[a[1] for a in settings.ADMINS],
            fail_silently=True
        )