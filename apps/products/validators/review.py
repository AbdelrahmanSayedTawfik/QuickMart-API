from django.core.exceptions import ValidationError
from apps.orders.models.order import Order


class ReviewValidator:

    @staticmethod
    def validate_purchased(user, product):
        
        has_purchased = Order.objects.filter(
            user=user,
            items__product=product,
            status__in=['paid', 'shipped', 'delivered']
        ).exists()
        
        if not has_purchased:
            raise ValidationError(
                'You can only review products you have purchased.'
            )
    
    @staticmethod
    def validate_rating(rating):
        if not (1 <= rating <= 5):
            raise ValidationError('Rating must be between 1 and 5.')