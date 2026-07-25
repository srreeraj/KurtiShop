# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<str:order_number>/', views.order_success, name='order_success'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('cancel/', views.order_lookup, name='order_lookup'),
    path('cancel/<str:order_number>/', views.order_cancel_detail, name='order_cancel_detail'),
    path('cancel/<str:order_number>/request/', views.request_cancellation, name='request_cancellation'),
]