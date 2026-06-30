from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.products.models.product import Product
from apps.products.models.product_image import ProductImage
from apps.products.serializers.product_image import (
    ProductImageSerializer,
    ProductImageUploadSerializer,
    BulkProductImageUploadSerializer,
)
from apps.products.permissions import IsAdminOrSeller

@extend_schema_view(
    
    post=extend_schema(
        tags=['Products Images'],                    
        summary='Upload single product image', 
        description='''
        Upload one image for a product.
        
        **Body:** multipart/form-data
        - `image` (file, required) - The image file
        - `alt_text` (string, optional) - SEO description
        - `is_main` (boolean, optional) - Set as primary image
        - `order` (integer, optional) - Display position
        
        **Rules:**
        - First image uploaded becomes main automatically
        - If is_main=true, all other images become non-main
        ''',
        request={
            'multipart/form-data': ProductImageUploadSerializer
        },
        responses={
            201: OpenApiResponse(
                response=ProductImageSerializer,
                description='Image uploaded successfully'
            ),
            400: OpenApiResponse(
                description='Invalid file or missing required field'
            ),
            404: OpenApiResponse(
                description='Product not found'
            ),
        }
    )
)
class ProductImageUploadView(generics.CreateAPIView):

    queryset = ProductImage.objects.all()
    serializer_class = ProductImageUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrSeller]

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404

        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        has_existing_images = ProductImage.objects.filter(product=product).exists()
        is_main = serializer.validated_data.get('is_main', False)

        if not has_existing_images:
            is_main = True

        if is_main:
            ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)

        
        if 'order' not in serializer.validated_data:
            next_order = ProductImage.objects.filter(product=product).count()
            serializer.save(product=product, is_main=is_main, order=next_order)
        else:
            serializer.save(product=product, is_main=is_main)



@extend_schema_view(
    post=extend_schema(
        tags=['Products Images'],
        summary='Upload multiple product images',
        description='''
        Upload multiple images at once with one request.
        
        **Body:** multipart/form-data
        - `images` (files, required) - Select multiple files
        - `alt_texts` (strings, optional) - One per image
        - `main_index` (integer, optional) - Which image is main (0=first)
        
        **Example:** Upload 3 images, set 2nd as main:
        ```
        images: [front.jpg, side.jpg, back.jpg]
        alt_texts: ["Front", "Side", "Back"]
        main_index: 1
        ```
        ''',
        request={
            'multipart/form-data': BulkProductImageUploadSerializer
        },
        responses={
            201: OpenApiResponse(
                response=ProductImageSerializer,  
                description='All images uploaded successfully'
            ),
            400: OpenApiResponse(
                description='Invalid data (e.g., main_index out of range)'
            ),
            404: OpenApiResponse(
                description='Product not found'
            ),
        }
    )
)
class ProductImageBulkUploadView(generics.CreateAPIView):

    serializer_class = BulkProductImageUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminOrSeller]

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with id {product_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        images = request.FILES.getlist('images')
        alt_texts = request.data.getlist('alt_texts') or []

        raw_main_index = request.data.get('main_index')
        main_index = int(raw_main_index) if raw_main_index not in (None, '') else None

        data = {
            'images': images,
            'alt_texts': alt_texts,
            'main_index': main_index,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)

        created_images = serializer.instance

        response_serializer = ProductImageSerializer(
            created_images,
            many=True,
            context={'request': request}
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        tags=['Products Images'],
        summary='List product images',
        description='Get all images for a specific product, ordered by display order.',
        responses={
            200: OpenApiResponse(
                response=ProductImageSerializer,
                description='Array of images'
            ),
        }
    )
)
class ProductImageListView(generics.ListAPIView):

    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrSeller]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return ProductImage.objects.filter(product_id=product_id).order_by('order')


@extend_schema_view(
    get=extend_schema(
        tags=['Products Images'],
        summary='Get image details',
        description='Retrieve a single image by its ID.',
    ),
    put=extend_schema(
        tags=['Products Images'],
        summary='Update image',
        description='Full update of image metadata (alt_text, is_main, order).',
    ),
    patch=extend_schema(
        tags=['Products Images'],
        summary='Partial update image',
        description='Update specific fields only.',
    ),
    delete=extend_schema(
        tags=['Products Images'],
        summary='Delete image',
        description='Remove image from product and delete file.',
    ),
)
class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    lookup_field = 'pk'
    permission_classes = [IsAdminOrSeller]
    
    def perform_update(self, serializer):

        is_main = serializer.validated_data.get('is_main')
        
        if is_main is True:
            product = serializer.instance.product
            ProductImage.objects.filter(
                product=product,
                is_main=True
            ).exclude(
                id=serializer.instance.id
            ).update(is_main=False)
            
        serializer.save()
    
    def perform_destroy(self, instance):

        was_main = instance.is_main
        instance.delete()

        if was_main:
            remaining = ProductImage.objects.filter(
                product=instance.product
            ).order_by('created_at').first()
            
            if remaining:
                remaining.is_main = True
                remaining.save(update_fields=['is_main'])