from django.urls import path
from .views import CustomerListView, OrderListView

urlpatterns = [
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]