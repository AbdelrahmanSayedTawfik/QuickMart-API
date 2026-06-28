from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample

from apps.products.models.category import Category
from apps.products.serializers.category import CategorySerializer
from apps.products.permissions import IsAdminOrReadOnly
from apps.products.services.cache import ProductCacheService
from apps.products.pagination import FlexibleProductPagination

@extend_schema_view(
    get=extend_schema(
        tags=['Categories'],
        summary='List all categories',
        description='Get all product categories. **Public endpoint** — no authentication required. Results are cached for 1 hour.',
        responses={
            200: OpenApiResponse(
                description='List of categories',
                examples=[OpenApiExample('Success', value=[{'id': 1, 'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices', 'image': 'https://...', 'is_active': True}])]
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
    pagination_class = FlexibleProductPagination
    permission_classes = [IsAdminOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        
        cached_data = ProductCacheService.get_category_list()
        if cached_data:
            return Response(cached_data)
        
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
        ProductCacheService.set_category_list(data)
        
        return Response(data)


@extend_schema_view(
    get=extend_schema(tags=['Categories'], summary='Get category details'),
    put=extend_schema(tags=['Categories'], summary='Update category', description='**Admin only.**'),
    patch=extend_schema(tags=['Categories'], summary='Partially update category', description='**Admin only.**'),
    delete=extend_schema(tags=['Categories'], summary='Delete category', description='**Admin only.**'),
)
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'