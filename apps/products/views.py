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

# Create your views here.

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  
    lookup_field = 'slug'


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
        
    
    

        
            
class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]  
    lookup_field = 'slug'    
    
    
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
    
    
class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [ IsAuthenticated, IsReviewerOrReadOnly]  
    
    
