from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Product, Order, OrderItem, Review
from .serializers import ProductSerializer, OrderSerializer, ReviewSerializer



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    
    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser] 
        return [permission() for permission in self.permission_classes]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return user.orders.all().order_by('-created_at') 

    @transaction.atomic 
    def perform_create(self, serializer):
        items_data = self.request.data.pop('items', [])
        order = serializer.save(owner=self.request.user, total_price=0)
        total_price = 0

        for item_data in items_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity', 1)

            product = get_object_or_404(Product, id=product_id)
            
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for product {product.name}. Available: {product.stock}"
                )
            item_price = product.price * quantity
            total_price += item_price

            OrderItem.objects.create(
                order=order, 
                product=product, 
                quantity=quantity, 
                price=product.price 
            )
            
            product.stock -= quantity
            product.save()

        order.total_price = total_price
        order.save()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
