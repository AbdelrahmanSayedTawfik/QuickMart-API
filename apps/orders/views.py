from decimal import Decimal
from django.shortcuts import render
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer , CheckoutSerializer, OrderSerializer, OrderStatusLogSerializer, OrderItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
class CartAddItemView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        from apps.products.models import Product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        if product.status != 'available':
            return Response({'error': 'Product is not available.'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        else:
            cart_item.quantity = int(quantity)
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)    
    
    
class CartRemoveItemView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')

        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)   
        
        
class CartUpdateItemView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id or quantity is None:
            return Response({'error': 'Product ID and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class CartClearItemsView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CheckoutView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer_class = CheckoutSerializer
        serializer_is_valid = serializer_class(data=request.data)
        cart = request.user.cart
        if not cart.items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        shipping_fee  = Decimal('50.00')  # Flat shipping fee for simplicity
        tax = Decimal('0.10')  # 10% tax for simplicity
        order = Order.objects.create(
            user=request.user,
            subtotal=cart.total,
            tax=cart.total * tax,
            total=cart.total + (cart.total * tax) + shipping_fee,
            shipping_fee=shipping_fee,
            delivery_address=serializer_is_valid.validated_data['delivery_address'],
            delivery_city=serializer_is_valid.validated_data['delivery_city'],
            delivery_phone=serializer_is_valid.validated_data['delivery_phone'],
            notes=serializer_is_valid.validated_data.get('notes', '')
        )
        
        for cart_item in cart.items.select_related('product').all():
            product = cart_item.product
            if product.status != 'available':
                order.delete()  # Rollback order creation
                return Response({'error': f'Product {product.name} is not available.'}, status=status.HTTP_400_BAD_REQUEST)
            if cart_item.quantity > product.stock_quantity:
                order.delete()  # Rollback order creation
                return Response({'error': f'Quantity for {product.name} exceeds available stock.'}, status=status.HTTP_400_BAD_REQUEST)
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                product_name=product.name,
                product_price=product.price,
                subtotal=product.price * cart_item.quantity,
                quantity=cart_item.quantity
            )
            # Reduce stock quantity
            product.stock_quantity -= cart_item.quantity
            # Update product status
            if product.stock_quantity <= 0:
                product.status = 'out_of_stock'
            product.save()
        # Clear Cart
        cart.items.all().delete()
        # Send confirmation email (via Celery - Day 5)
        # (Implementation for sending email via Celery would go here)


        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')  

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        order_number = kwargs.get('order_number')
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            
            
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.status != 'pending':
            return Response({'error': 'Only pending orders can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        # Restore stock quantity for each order item
        for item in order.items.select_related('product').all():
            product = item.product
            if product:
                product.stock_quantity += item.quantity
                # Update product status
                if product.stock_quantity > 0 and product.status == 'out_of_stock':
                    product.status = 'available'
                product.save()
                
        order.status = 'cancelled'
        order.save()
        
        return Response({'message': 'Order cancelled successfully.'}, status=status.HTTP_200_OK)
