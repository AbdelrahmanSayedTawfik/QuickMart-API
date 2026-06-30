from django.db.models import QuerySet, Avg, Count, Q


class ProductQuerySet(QuerySet):
    def active(self):
        return self.filter(status='available')
    
    def in_stock(self):
        return self.filter(stock_quantity__gt=0)
    
    def featured(self):
        return self.filter(is_featured=True)
    
    def by_category_tree(self, category):
        from apps.products.models.category_tree import CategoryTree
        category_ids = CategoryTree.objects.filter(
            category_above=category
        ).values_list('category_below_id', flat=True)
        return self.filter(category_id__in=category_ids, is_active=True)
    
    def with_stats(self):
        return self.annotate(
            avg_rating=Avg('reviews__rating'),
            total_reviews=Count('reviews')
        )
    
    def search(self, query):
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    def price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs
    
    def optimized(self):
        return self.select_related('seller', 'category').prefetch_related('images', 'reviews')
    
    