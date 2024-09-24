from django.urls import path
from .views import CustomerListView, OrderListView, LoginAPIView

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('login/', LoginAPIView.as_view(), name='login'),
]