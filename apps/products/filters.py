import django_filters
from apps.products.models.product import Product 
from apps.products.models.category import Category
from apps.products.models.category_tree import CategoryTree
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class ProductFilter(django_filters.FilterSet):
    
    # Price Range filters
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name='price')
    
    # Category filter (including subcategories, accepts slug or id)
    category = django_filters.CharFilter(method='filter_by_category')
    
    # Multiple choice filters
    status_in = django_filters.MultipleChoiceFilter(
        field_name='status', 
        choices=Product.STATUS_CHOICES,
        lookup_expr='in'
    )    
    stock_status_in = django_filters.MultipleChoiceFilter(
        field_name='stock_status', 
        choices=Product.STOCK_STATUS_CHOICES,
        lookup_expr='in'
    )
    
    # Search filter
    search = django_filters.CharFilter(method='filter_by_search')
    
    # Rating filters
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    rating_range = django_filters.RangeFilter(field_name='rating')
    
    # Boolean filters
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    is_on_stock = django_filters.BooleanFilter(method='filter_by_stock')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_range = django_filters.DateTimeFromToRangeFilter(field_name='created_at')
    
    # Exclude filters
    exclude_category = django_filters.NumberFilter(field_name='category', exclude=True)    
    
    class Meta:
        model = Product
        fields = ['is_active']
    
    
    def __init__(self, data=None, *args, **kwargs):
        # Clean empty values from query params before processing
        if data:
            data = {k: v for k, v in data.items() if v not in ('', None)}
        
        super().__init__(data=data, *args, **kwargs)
    
    def filter_by_category(self, queryset, name, value):
        try:
            if value.isdigit():
                filter_kwargs = {'id': int(value), 'is_active': True}
            else:
                filter_kwargs = {'slug': value, 'is_active': True}
            category = Category.objects.get(**filter_kwargs)

            # Get descendants + include the category itself
            descendant_ids = (
                CategoryTree.objects
                .filter(category_above=category)
                .filter(category_below__is_active=True)
                .values_list('category_below_id', flat=True)
            )
        
            # Combine parent + descendants
            category_ids = list(descendant_ids) + [category.id]

            return queryset.filter(category_id__in=category_ids)

        except Category.DoesNotExist:
            return queryset.none()
        
    def filter_by_search(self, queryset, name, value):
        return queryset.filter( 
            Q(name__icontains=value) | 
            Q(description__icontains=value) |
            Q(seller__username__icontains=value) |
            Q(category__name__icontains=value)
        ).distinct()
        
    def filter_by_stock(self, queryset, name, value):
        if value:
            # is_on_stock = True: in stock AND available
            return queryset.filter(stock_quantity__gt=0, status='available')
        else:
            # is_on_stock = False: either no stock OR not available
            return queryset.filter(
                Q(stock_quantity=0) | ~Q(status='available')
            )