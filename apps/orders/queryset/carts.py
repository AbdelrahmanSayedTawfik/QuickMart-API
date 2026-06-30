from django.db.models import QuerySet, Sum, Prefetch, F


class CartQuerySet(QuerySet):

    def with_items(self):
        
        return self.prefetch_related(
            Prefetch(
                'items',
                queryset=self.model.items.related_model.objects.select_related('product')
            )
        )
    
    def for_user(self, user_id):
        
        return self.filter(user_id=user_id)
    
    def with_totals(self):
        
        return self.annotate(
            total_items=Sum('items__quantity'),
            total_value=Sum(F('items__quantity') * F('items__product__price'))
        )


