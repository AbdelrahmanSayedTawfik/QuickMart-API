from django.db import models
from apps.accounts.models.user import CustomUser
from django.utils import timezone

class BaseModel(models.Model):
    #created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        abstract = True
    
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)  
    
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()
        
        
# mixins model Just onlyyy Methods Not anything else 

class CouponValidationMixin:

    def is_valid_for_order(self, order_total):
        from django.utils import timezone

        if self.is_deleted:
            return False, "Coupon no longer exists"

        if not self.is_active:
            return False, "Coupon is not active"

        if self.expires_at < timezone.now():
            return False, "Coupon has expired"

        if self.times_used >= self.max_uses:
            return False, "Coupon has reached its usage limit"

        if order_total < self.min_order_amount:
            return False, f"Minimum order amount is {self.min_order_amount}"

        return True, "Valid"

    def calculate_discount(self, order_total):
        return round(float(order_total) * float(self.discount_percent) / 100, 2)

    def apply(self, order_total):
        is_valid, message = self.is_valid_for_order(order_total)
        if not is_valid:
            raise ValueError(message)
        self.times_used += 1
        self.save(update_fields=['times_used'])
        return self.calculate_discount(order_total)        