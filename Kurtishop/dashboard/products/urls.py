from django.urls import path
from . import views

app_name = "dashboard_products"

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/edit/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # AJAX helpers
    path('ajax/variant-row/', views.get_variant_row, name='variant_row'),
    path('ajax/image-preview/', views.image_preview, name='image_preview'),
]