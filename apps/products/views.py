from django.shortcuts import render
from .models import Category, Product, ProductImage, Review
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ReviewSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly , IsSellerOrReadOnly , IsOwnerOrReadOnly, IsReviewerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)

# Create your views here.
@extend_schema_view(
    get=extend_schema(
        tags=['Categories'],
        summary='List all categories',
        description='''
        Get all product categories.
        
        **Public endpoint** — no authentication required.
        Results are cached for 1 hour.
        ''',
        responses={
            200: OpenApiResponse(
                description='List of categories',
                examples=[
                    OpenApiExample(
                        'Success',
                        value=[
                            {
                                'id': 1,
                                'name': 'Electronics',
                                'slug': 'electronics',
                                'description': 'Electronic devices',
                                'image': 'https://...',
                                'is_active': True
                            }
                        ]
                    )
                ]
            )
        }
    ),
    post=extend_schema(
        tags=['Categories'],
        summary='Create category',
        description='Create a new product category. **Admin only.**',
        request=CategorySerializer,
        responses={
            201: OpenApiResponse(description='Category created'),
            403: OpenApiResponse(description='Permission denied — admin only'),
        }
    )
)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def list (self, request, *args, **kwargs):
        cache_key = 'category_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*60)  # Cache for 1 hour
        return Response(serializer.data)

    
@extend_schema_view(
    get=extend_schema(
        tags=['Categories'],
        summary='Get category details',
        description='Get a single category by slug.',
    ),
    put=extend_schema(
        tags=['Categories'],
        summary='Update category',
        description='Update category. **Admin only.**',
    ),
    patch=extend_schema(
        tags=['Categories'],
        summary='Partially update category',
        description='Partial update. **Admin only.**',
    ),
    delete=extend_schema(
        tags=['Categories'],
        summary='Delete category',
        description='Delete category. **Admin only.**',
    )
)
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  
    lookup_field = 'slug'

@extend_schema_view(
    get=extend_schema(
        tags=['Products'],
        summary='List products',
        description='''
        Get paginated list of products with filtering, search, and ordering.
        
        **Public endpoint** — no authentication required.
        
        **Query Parameters:**
        - `category` — Filter by category slug
        - `min_price` / `max_price` — Price range filter
        - `search` — Search in name and description
        - `ordering` — Order by `price`, `-price`, `created_at`, `-created_at`
        - `page` — Page number for pagination
        
        **Cached** — results cached per unique query for 1 hour.
        ''',
        parameters=[
            OpenApiParameter(name='category', description='Filter by category slug', required=False, type=str),
            OpenApiParameter(name='min_price', description='Minimum price', required=False, type=float),
            OpenApiParameter(name='max_price', description='Maximum price', required=False, type=float),
            OpenApiParameter(name='search', description='Search term', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order field (prefix with - for descending)', required=False, type=str),
            OpenApiParameter(name='page', description='Page number', required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(
                description='Paginated product list',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'count': 150,
                            'next': 'http://localhost:8000/api/products/?page=2',
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'name': 'iPhone 15 Pro',
                                    'slug': 'iphone-15-pro',
                                    'price': '999.99',
                                    'stock_quantity': 50,
                                    'status': 'available',
                                    'category': 'electronics',
                                    'seller': 'seller1'
                                }
                            ]
                        }
                    )
                ]
            )
        }
    ),
    post=extend_schema(
        tags=['Products'],
        summary='Create product',
        description='''
        Create a new product. **Seller only.**
        
        Seller is automatically set from authenticated user.
        ''',
        request=ProductSerializer,
        responses={
            201: OpenApiResponse(description='Product created'),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied — sellers only'),
        }
    )
)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSellerOrReadOnly()]
        return [AllowAny()]
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
        
    def list (self, request, *args, **kwargs):
        
        query_string = request.query_params.urlencode()
        cache_key = f'product_list_{query_string}' if query_string else 'product_list_all'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
        cache.set(cache_key, data, timeout=60*60)  # Cache for 1 hour
        return Response(data)    


@extend_schema_view(
    get=extend_schema(
        tags=['Products'],
        summary='Get product details',
        description='Get a single product by slug.',
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
        cache_key = f'product_detail_{slug}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, timeout=60*60)  # Cache for 1 hour
        return Response(serializer.data)
    


@extend_schema_view(
    get=extend_schema(
        tags=['Reviews'],
        summary='List product reviews',
        description='''
        Get verified reviews for a product.
        
        **Public endpoint** — no authentication required.
        Only shows reviews from verified purchasers.
        ''',
        parameters=[
            OpenApiParameter(name='slug', location=OpenApiParameter.PATH, description='Product slug', required=True, type=str),
        ],
        responses={
            200: OpenApiResponse(description='List of reviews'),
        }
    ),
    post=extend_schema(
        tags=['Reviews'],
        summary='Create review',
        description='''
        Add a review for a product. **Authenticated users only.**
        
        User must have purchased the product to review.
        ''',
        request=ReviewSerializer,
        responses={
            201: OpenApiResponse(description='Review created'),
            400: OpenApiResponse(description='Validation error or not purchased'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
)    
class ReviewListCreateView(generics.ListCreateAPIView):
    
    serializer_class = ReviewSerializer
    def get_queryset(self):
        slug = self.kwargs['slug']
        return Review.objects.filter(slug=slug, is_verified_purchaser=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def perform_create(self, serializer):
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        serializer.save(user=self.request.user, product=product, is_verified_purchaser=True)
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        context['product'] = product
        return context
    


@extend_schema_view(
    get=extend_schema(tags=['Reviews'], summary='Get review'),
    put=extend_schema(tags=['Reviews'], summary='Update review', description='**Reviewer only.**'),
    patch=extend_schema(tags=['Reviews'], summary='Partial update', description='**Reviewer only.**'),
    delete=extend_schema(tags=['Reviews'], summary='Delete review', description='**Reviewer only.**'),
)    
class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [ IsAuthenticated, IsReviewerOrReadOnly]  
    
    
