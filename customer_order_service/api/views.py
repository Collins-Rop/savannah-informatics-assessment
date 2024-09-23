from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer
import africastalking
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
import os

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