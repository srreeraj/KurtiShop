from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path('verify/', views.verify_payment, name="verify_payment"),
    path('webhook/',views.razorpay_webhook, name="razorpay_webhook"),
]