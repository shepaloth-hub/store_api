From rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product,Order,OrderItem,Review
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields =['id','name','description','price','stock','created_at']

class OrderSerializer(serializers.ModelSerializer):
    owner= serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Order
        fields = ['id','owner','total_price','status','created_at']

class OrderItemSerializer(serializers.ModelSerializer):
      order=OrderSerializer(read_only=True)
      product=ProductSerializer(read_only=True)
      class Meta:
          model = OrderItem
          fields = ['id','product','order','quantity','price']
class ReviewSerializer(serializers.ModelSerializer):
      user=serializers.ReadOnlyField(source='user.username')
      class Meta:
       model = Review
       fields = ['id','user','rating','comment','created_at']
