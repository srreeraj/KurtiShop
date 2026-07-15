from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('drawer/', views.cart_drawer, name='cart_drawer'),
    path('add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('count/', views.get_cart_count, name='cart_count'),
]