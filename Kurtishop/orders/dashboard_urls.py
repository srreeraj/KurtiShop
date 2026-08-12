from django.urls import path
from . import dashboard_views as views

app_name = "orders_dashboard"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("<str:order_number>/", views.order_detail, name="order_detail"),
    path("<str:order_number>/invoice/", views.download_invoice, name="download_invoice"),
    path(
        "<str:order_number>/return/<int:return_id>/fulfill-exchange/",
        views.fulfill_exchange,
        name="fulfill_exchange",
    ),
]