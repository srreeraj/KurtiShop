from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.dashboard_login, name="login"),
    path("", views.dashboard_home, name="home"),
    path("logout/", views.dashboard_logout, name="logout"),
]