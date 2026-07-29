from django.urls import path
from . import lookup_views as views

app_name = "lookups"

urlpatterns = [
    # Occasion
    path("occasions/", views.occasion_list, name="occasion_list"),
    path("occasions/create/", views.occasion_create, name="occasion_create"),
    path("occasions/<int:pk>/edit/", views.occasion_edit, name="occasion_edit"),
    path("occasions/<int:pk>/delete/", views.occasion_delete, name="occasion_delete"),

    # Color
    path("colors/", views.color_list, name="color_list"),
    path("colors/create/", views.color_create, name="color_create"),
    path("colors/<int:pk>/edit/", views.color_edit, name="color_edit"),
    path("colors/<int:pk>/delete/", views.color_delete, name="color_delete"),

    # Size
    path("sizes/", views.size_list, name="size_list"),
    path("sizes/create/", views.size_create, name="size_create"),
    path("sizes/<int:pk>/edit/", views.size_edit, name="size_edit"),
    path("sizes/<int:pk>/delete/", views.size_delete, name="size_delete"),
]