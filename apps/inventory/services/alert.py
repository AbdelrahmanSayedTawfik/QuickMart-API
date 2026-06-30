from django.db import transaction
from django.utils import timezone

from apps.products.models.product import Product
from apps.inventory.models.stock_alert import StockAlert


class AlertService:

    DEFAULT_LOW_STOCK_THRESHOLD = 10

    @staticmethod
    def check_and_create_alerts(product: Product) -> list:
        """
        Call this from Product.save() to auto-generate alerts.
        """
        alerts = []

        # Don't alert for draft or inactive products
        if product.status == 'draft' or not product.is_active:
            return alerts

        stock = product.stock_quantity

        # ── OUT OF STOCK ──
        if stock == 0:
            existing = StockAlert.objects.filter(
                product=product,
                alert_type='out_of_stock',
                is_resolved=False
            ).exists()

            if not existing:
                alert = StockAlert.objects.create(
                    product=product,
                    alert_type='out_of_stock',
                    stock_at_trigger=stock,
                    threshold=0
                )
                alerts.append(alert)

        # ── LOW STOCK ──
        elif 0 < stock < AlertService.DEFAULT_LOW_STOCK_THRESHOLD:
            existing = StockAlert.objects.filter(
                product=product,
                alert_type='low_stock',
                is_resolved=False
            ).exists()

            if not existing:
                alert = StockAlert.objects.create(
                    product=product,
                    alert_type='low_stock',
                    stock_at_trigger=stock,
                    threshold=AlertService.DEFAULT_LOW_STOCK_THRESHOLD
                )
                alerts.append(alert)

        # ── BACK IN STOCK ──
        # If we have stock now, resolve any old out_of_stock alerts
        if stock > 0:
            old_alert = StockAlert.objects.filter(
                product=product,
                alert_type='out_of_stock',
                is_resolved=False
            ).first()

            if old_alert:
                old_alert.resolve(user=None, note='Stock replenished automatically')

                # Create back_in_stock alert only if we resolved an old one
                alert = StockAlert.objects.create(
                    product=product,
                    alert_type='back_in_stock',
                    stock_at_trigger=stock,
                    threshold=0
                )
                alerts.append(alert)

        return alerts

    @staticmethod
    def get_unresolved_alerts():
        return StockAlert.objects.filter(is_resolved=False)

    @staticmethod
    def get_alert_summary():
        from django.db.models import Count

        return {
            'total_unresolved': StockAlert.objects.filter(is_resolved=False).count(),
            'low_stock': StockAlert.objects.filter(
                alert_type='low_stock', is_resolved=False
            ).count(),
            'out_of_stock': StockAlert.objects.filter(
                alert_type='out_of_stock', is_resolved=False
            ).count(),
            'back_in_stock': StockAlert.objects.filter(
                alert_type='back_in_stock', is_resolved=False
            ).count(),
        }

    @staticmethod
    @transaction.atomic
    def resolve_alert(alert_id: int, user, note: str = '') -> StockAlert:
        alert = StockAlert.objects.get(id=alert_id)
        alert.resolve(user=user, note=note)
        return alert