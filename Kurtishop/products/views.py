from django.shortcuts import render, get_object_or_404
from .models import Product
from categories.models import Category

# Create your views here.

def product_list(request):
    products = Product.objects.filter(
        is_active=True,
        is_deleted=False
    ).select_related('category').prefetch_related('images','variants')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        active_category = Category.objects.filter(slug=category_slug).first()
    else:
        active_category = None

    from django.core.paginator import Paginator
    paginator = Paginator(products, 12) #12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        'products' : products,
        'categories' : Category.objects.filter(is_active=True, is_deleted=False),
        'active_category' : active_category,
    }

    return render(
        request,
        'products/product_list.html',
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
