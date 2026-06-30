from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter

from apps.products.models.product import Product
from apps.products.serializers.product import ProductSerializer , ProductListSerializer
from apps.products.permissions import IsSellerOrAdminOrReadOnly, IsOwnerOrReadOnly
from apps.products.querysets.products import ProductQuerySet
from apps.products.services.product import ProductService
from apps.products.services.cache import ProductCacheService
from apps.products.filters import ProductFilter
from apps.products.pagination import StandardProductPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


@extend_schema_view(
    get=extend_schema(
        tags=['Products'],
        summary='List products',
        description='''
        Get paginated products with advanced filtering.
        
        **Query Parameters:**
        - `page` / `page_size` — Pagination
        - `min_price` / `max_price` — Price range
        - `category` — Filter by category (includes subcategories!)
        - `search` — Search in name, description, seller
        - `is_featured` — Featured products only
        - `min_rating` — Minimum rating (1-5)
        - `ordering` — Sort by price, -price, created_at, -created_at, rating, sales_count
        ''',
        parameters=[
            OpenApiParameter(name='page', type=int, description='Page number'),
            OpenApiParameter(name='page_size', type=int, description='Items per page (max 100)'),
            OpenApiParameter(name='min_price', type=float, description='Minimum price'),
            OpenApiParameter(name='max_price', type=float, description='Maximum price'),
            OpenApiParameter(name='category', type=int, description='Category ID (includes subcategories)'),
            OpenApiParameter(name='search', type=str, description='Search term'),
            OpenApiParameter(name='is_featured', type=bool, description='Featured only'),
            OpenApiParameter(name='min_rating', type=float, description='Minimum rating 1-5'),
            OpenApiParameter(name='ordering', type=str, description='Sort field (- for desc)'),
        ],
    ),
    post=extend_schema(
        tags=['Products'],
        summary='Create product',
        description='Seller only. Seller auto-set from authenticated user.',
    )
)
class ProductListCreateView(generics.ListCreateAPIView):

    filterset_class = ProductFilter
    pagination_class = StandardProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'rating', 'sales_count']
    
    def get_permissions(self):
        
        if self.request.method == 'POST':
            return [IsSellerOrAdminOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        return Product.objects.active().optimized()
    
    def get_serializer_class(self):

        if self.request.method == 'GET':  # ← For GET list
            return ProductListSerializer
        return ProductSerializer  # ← For POST create
    
    def list(self, request, *args, **kwargs):

        # Build cache key from query params
        query_string = request.query_params.urlencode()
        cached_data, cache_key = ProductCacheService.get_product_list(query_string)
        
        if cached_data:
            return Response(cached_data)
        
        # Standard DRF list flow
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        
        # Cache result
        ProductCacheService.set_product_list(cache_key, data)
        
        return Response(data)
    
    def perform_create(self, serializer):
        
        data = serializer.validated_data.copy()
        data.pop('seller', None)  
    
        ProductService.create_product(
            data=data,
            seller=self.request.user
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Products'],
        summary='Get product details',
        description='Get a single product by slug. Cached for 1 hour.',
    ),
    put=extend_schema(
        tags=['Products'],
        summary='Update product',
        description='Update product. **Owner only.**',
    ),
    patch=extend_schema(
        tags=['Products'],
        summary='Partially update product',
        description='Partial update. **Owner only.**',
    ),
    delete=extend_schema(
        tags=['Products'],
        summary='Delete product',
        description='Delete product. **Owner only.**',
    )
)
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):

        slug = kwargs.get('slug')
        cached_data, cache_key = ProductCacheService.get_product_detail(slug)
        
        if cached_data:
            return Response(cached_data)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        ProductCacheService.set_product_detail(cache_key, serializer.data)
        
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        serializer.save()  
    
    def perform_destroy(self, instance):

        ProductService.delete_product(instance)