import django_filters
from .models import Product, Category
from django.db.models import Q , Avg, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class ProductFilter(django_filters.FilterSet):
    
    # Price Rang filters:
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    # price_min=100
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Rang Price filters:
    price_range = django_filters.RangeFilter(field_name='price')
    
    # Category filter (including subcategories):
    category = django_filters.NumberFilter(method='filter_by_category')
    
    def filter_by_category(self, queryset, name, value):
        try:
            category = Category.objects.get(id=value, is_active=True)
            descendant_ids = category.get_descendants
            return queryset.filter(category_id__in=descendant_ids)
        except Category.DoesNotExist:
            return queryset.none()
        
    # Multiple choice filters:
    status_in = django_filters.MultipleChoiceFilter(field_name='status', choices=Product.STATUS_CHOICES,lookup_expr='in')    
    stock_status_in = django_filters.MultipleChoiceFilter(field_name='stock_status', choices=Product.STOCK_STATUS_CHOICES,lookup_expr='in')
    
    
    # Search filter (searches name and description and seller):
    search = django_filters.CharFilter(method='filter_by_search')
    def filter_by_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) |
            Q(seller__username__icontains=value)|
            Q(category__name__icontains=value)
        ).distinct()
        
        
    #rating filter:
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    rating_range = django_filters.RangeFilter(field_name='rating')
    
    #Boolean filters:
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    is_on_stock = django_filters.BooleanFilter(method='filter_by_stock')
    def filter_by_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0, stock_status__in=['in_stock'])
        else:
            return queryset.filter(stock_quantity=0)
        
        
    #Date filters:
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_range = django_filters.DateTimeFromToRangeFilter(field_name='created_at')
    
    #Exclude filters:
    exclude_category = django_filters.NumberFilter(field_name='category', exclude=True)    
    
    class Meta:
        model = Product
        fields = [ 'status', 'stock_status', 'is_active']
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            active_categories = Category.objects.filter(
                is_active=True
            ).values_list('id', 'name')

            self.filters['category'].extra['choices'] = active_categories
            
        