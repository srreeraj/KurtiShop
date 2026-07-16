from django.shortcuts import render
from products.models import Product
from categories.models import Category
from django.db.models import Count, Q

# Create your views here.

def home(request):

    categories = Category.objects.filter(
        is_active = True,
        is_deleted = False,
    ).annotate(
        product_count=Count('products', filter=Q(products__is_active=True, product__is_deleted=False))
    ).order_by('name')[:12]

    featured_products = Product.objects.filter(
        is_featured = True,
        is_active = True,
        is_deleted = False,
    ).select_related('category')[:8]

    new_arrivals = Product.objects.filter(
        is_new_arrival = True,
        is_active =True,
        is_deleted = False,
    ).select_related('category')[:8]

    context = {
        'categories' : categories,
        'featured_products' : featured_products,
        'new_arrivals' : new_arrivals
    }
    return render(request, 'core/home.html', context)