from django.urls import path
from . import dashboard_views as views

app_name = "products_dashboard"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("create/", views.product_create, name="product_create"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("pincodes/", views.pincode_list, name="pincode_list"),
    path("pincodes/create/", views.pincode_create, name="pincode_create"),
    path("pincodes/<int:pk>/edit/", views.pincode_edit, name="pincode_edit"),
    path("pincodes/<int:pk>/delete/", views.pincode_delete, name="pincode_delete"),
]