# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
]