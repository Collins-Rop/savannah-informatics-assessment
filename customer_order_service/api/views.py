from tokenize import Token
from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Customer, Order
from .serializers import CustomerSerializer, LoginSerializer, OrderSerializer
import africastalking
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.cache import cache
import os
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

# class LoginView(APIView):
    #  permission_classes = [permissions.AllowAny]


    #  def post(self, request, *args, **kwargs):
    #     serializer = AuthTokenSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data['user']
    #     token, created = Token.objects.get_or_create(user=user)
    #     return Response({
    #         'token': token.key,
    #         'user_id': user.id
    #     })
class LoginAPIView(APIView):
    serializer_class = LoginSerializer
    authentication_classes = [TokenAuthentication] 

    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(username=serializer.data['username'], password=serializer.data['password']) 
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': [token.key], "Success":"Login Successfull"}, status=status.HTTP_201_CREATED ) 
            return Response({'Message': 'Invalid Username and Password'}, status=401)
class CustomerListView(APIView):
    permission_classes = [permissions.AllowAny]


    def get(self, request):
        
        cache_key = f'customers_{request.GET.urlencode()}'
        customers = cache.get(cache_key)
        if not customers:
            customers = Customer.objects.all()
            cache.set(cache_key, customers, 60)  
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class OrderListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cache_key = f'orders_{request.GET.urlencode()}'
        orders = cache.get(cache_key)
        if not orders:
            orders = Order.objects.all()
            cache.set(cache_key, orders, 60)  
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def perform_create(self, serializer):
        order = serializer.save()
        self.send_sms_notification(order)

    def send_sms_notification(self, order):
        username = os.environ.get("AFRICASTALKING_USERNAME")
        api_key = os.environ.get("AFRICASTALKING_API_KEY")
        africastalking.initialize(username, api_key)

        sms = africastalking.SMS

        message = f"Dear {order.customer.name}, your order for {order.item} has been received. Total amount: {order.amount}"

        try:
            sms.send(message, [order.customer.phone_number])
        except Exception as e:
            print(f"Error sending SMS: {e}")