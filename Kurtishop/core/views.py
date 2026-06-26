from django.shortcuts import render
from products.models import Product

# Create your views here.

def home(request):
    featured_products = Product.objects.filter(
        is_featured = True,
        is_active = True,
        is_deleted = False,
    )[:8]

    new_arrivals = Product.objects.filter(
        is_new_arrival = True,
        is_active =True,
        is_deleted = False,
    )[:8]

    context = {
        'featured_products' : featured_products,
        'new_arrivals' : new_arrivals
    }
    return render(request, 'core/home.html')