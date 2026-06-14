from django.db.models import QuerySet
from apps.accounts.models.user import CustomUser

class CustomUserQuerySet(QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def by_email(self, email: str):
        return self.filter(email=email).first()

    def by_username(self, username: str):
        return self.filter(username=username).first()
    
    def seller (self, role: str):
        return self.filter(role='seller')
    def customer (self, role: str):
        return self.filter(role='customer')
    
    def with_cart(self):
        return self.prefetch_related('cart','cart__items','cart_items__product')
    
CustomUser.objects = CustomUserQuerySet.as_manager()    