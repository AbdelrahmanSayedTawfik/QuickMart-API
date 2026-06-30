from rest_framework import serializers
from apps.products.models.product_image import ProductImage

class ProductImageSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage              
        
        fields = ['id','product','image','image_url','alt_text','is_main','order','created_at']
        
        read_only_fields = ['id','created_at','image_url']

    def get_image_url(self, obj):
        
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['id','image','alt_text','is_main','order','created_at']
        
        read_only_fields = ['id','created_at']


class BulkProductImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), help_text='Select multiple image files')
    alt_texts = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False, help_text='Alt text for each image, in same order as images')
    main_index = serializers.IntegerField(required=False, allow_null=True, default=None, min_value=0)

    def validate(self, attrs):
        images = attrs.get('images', [])
        alt_texts = attrs.get('alt_texts', [])
        main_index = attrs.get('main_index')

        if main_index is not None and images and main_index >= len(images):
            raise serializers.ValidationError(
                f'main_index ({main_index}) must be less than number of images ({len(images)})'
            )
        while len(alt_texts) < len(images):
            alt_texts.append('')
        attrs['alt_texts'] = alt_texts[:len(images)]

        return attrs

    def create(self, validated_data):
        images = validated_data['images']
        alt_texts = validated_data['alt_texts']
        main_index = validated_data['main_index']
        product = validated_data['product']

        created_images = []

        has_existing_images = ProductImage.objects.filter(product=product).exists()
        existing_max_order = ProductImage.objects.filter(product=product).count()

        if not has_existing_images and images:
            main_index = main_index if main_index is not None else 0

        if main_index is not None and images:
            ProductImage.objects.filter(product=product, is_main=True).update(is_main=False)

        for index, image_file in enumerate(images):
            is_main = (index == main_index)

            image = ProductImage.objects.create(
                product=product,
                image=image_file,
                alt_text=alt_texts[index],
                is_main=is_main,
                order=existing_max_order + index,  
            )

            created_images.append(image)

        return created_images