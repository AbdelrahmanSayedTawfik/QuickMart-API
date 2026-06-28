
from django.db.models import QuerySet, Q,F
from django.utils import timezone


class CouponQuerySet(QuerySet):

    def active(self):
        
        return self.filter(is_deleted=False, is_active=True)

    def deleted(self):
        
        return self.filter(is_deleted=True)

    def not_deleted(self):
        
        return self.filter(is_deleted=False)

    def valid(self):
        
        return self.active().filter(
            expires_at__gt=timezone.now()
        ).filter(

            times_used__lt=F('max_uses')
        )

    def expired(self):
        return self.filter(expires_at__lte=timezone.now())

    def fully_used(self):
        
        return self.filter(times_used__gte=F('max_uses'))

    def by_min_discount(self, percent):
        return self.filter(discount_percent__gte=percent)