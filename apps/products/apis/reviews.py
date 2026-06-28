from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter

from apps.products.models.review import Review
from apps.products.models.product import Product
from apps.products.serializers.review import ReviewSerializer
from apps.products.permissions import IsReviewerOrReadOnly
from apps.products.validators.review import ReviewValidator
from apps.products.pagination import ProductFeedPagination
from apps.products.permissions import IsReviewerOrReadOnly

@extend_schema_view(
    get=extend_schema(
        tags=['Reviews'],
        summary='List product reviews',
        description='Get verified reviews for a product. **Public endpoint** — no authentication required. Only shows reviews from verified purchasers.',
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
        description='Add a review for a product. **Authenticated users only.** User must have purchased the product to review.',
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
    pagination_class = ProductFeedPagination
    
    def get_queryset(self):
        slug = self.kwargs['slug']
        return Review.objects.filter(
            product__slug=slug,
            is_verified_purchaser=True,
        ).order_by('-created_at')  
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsReviewerOrReadOnly()]
        return [AllowAny()]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        slug = self.kwargs['slug']
        context['product'] = Product.objects.get(slug=slug)
        return context
    
    def perform_create(self, serializer):
        slug = self.kwargs['slug']
        product = Product.objects.get(slug=slug)
        ReviewValidator.validate_purchased(self.request.user, product)
        serializer.save(
            user=self.request.user,
            product=product,
            is_verified_purchaser=True
        )
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=['Reviews'], summary='Get review'),
    put=extend_schema(tags=['Reviews'], summary='Update review', description='**Reviewer only.**'),
    patch=extend_schema(tags=['Reviews'], summary='Partial update', description='**Reviewer only.**'),
    delete=extend_schema(tags=['Reviews'], summary='Delete review', description='**Reviewer only.**'),
)
class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]