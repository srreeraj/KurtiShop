from django.shortcuts import render, get_object_or_404
from .models import Product

# Create your views here.

def product_list(request):
    products = Product.object.filter(
        is_active=True,
        is_deleted=False
    )

    context = {
        'product' : products
    }

    return render(
        request,
        'product/product_list.html',
        context
    )

def product_detail(request,slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True,
        is_deleted=False,
    )

    context = {
        'product' : product
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )
