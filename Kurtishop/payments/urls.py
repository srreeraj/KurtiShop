from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('initiate/<str:order_number>', views.initiate_payment, name="initiate_payment"),
    path('webhook/',views.razorpay_webhook, name="razorpay_webhook"),
]