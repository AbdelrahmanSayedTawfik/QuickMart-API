from django.db import models
from django.utils import timezone
from apps.products.models.base import BaseModel
from apps.products.querysets.coupon_queryset import CouponQuerySet
from apps.products.models.base import CouponValidationMixin

# CONCERT MODEL Inhirt from abstract model(BaseModel)

class Coupon(BaseModel,CouponValidationMixin):
    code = models.CharField(max_length=50,unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    objects= CouponQuerySet.as_manager()
    
    def __str__(self):
        return self.code
    
    
# Proxy  Models inheirt from Concert Model do some modification on it dont have table in db the same as concert table 

class ValidCouponManager(models.Manager):
    def get_queryset(self):
        return CouponQuerySet(self.model, using=self._db).valid()


class ExpiredCouponManager(models.Manager):
    def get_queryset(self):
        return CouponQuerySet(self.model, using=self._db).expired()


class ValidCoupon(Coupon):

    objects = ValidCouponManager()

    class Meta:
        proxy = True

    def apply_to_order(self, order_total):
        if order_total < self.min_order_amount:
            return None  # order too small
        discount = order_total * (self.discount_percent / 100)
        return round(order_total - discount, 2)


class ExpiredCoupon(Coupon):

    objects = ExpiredCouponManager()

    class Meta:
        proxy = True

    def days_since_expiry(self):
        return (timezone.now() - self.expires_at).days    