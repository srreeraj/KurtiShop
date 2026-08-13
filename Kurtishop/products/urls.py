from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.product_list,
        name='product_list'
    ),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('check-pincode/', views.check_pincode, name='check_pincode'),
    path(
        '<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),
]